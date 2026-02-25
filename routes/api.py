from flask import Blueprint, request, jsonify
from decimal import Decimal
from datetime import datetime
from sqlalchemy import text
from services.predict_service import predict_energy_service
from services.update_data_api import (
    fetch_data_from_api,
    upload_data_from_files,
    get_data_stats,
    get_energy_data,
    get_gdp_data
)

from services.data_validator import validate_data_compatibility, get_data_alignment_report
from services.train_service import retrain_model
from services.database_service import (
    get_training_history,
    get_data_update_history,
    get_prediction_history,
    save_prediction_history,
    get_history_summary,
    clear_all_history,
    init_database,
    get_active_model,
    get_candidate_models,
    activate_model,
    delete_candidate_model,
    get_all_models_comparison
)
from services.data_mysql_service import (
    get_energy_from_db,
    get_gdp_from_db,
    get_data_stats_from_db
)

api_bp = Blueprint("api", __name__)

@api_bp.route("/predict", methods=["POST"])
def predict():
    data = request.json
    scenario = data.get("scenario")
    
    years = int(data.get("years", data.get("forecast_years", 3)))  # Support both params
    save_to_db = data.get("save_to_database", True)  # Default True untuk backward compatibility

    if scenario not in ["optimis", "moderat", "pesimistis"]:
        return jsonify({"error": "Invalid scenario"}), 400

    if years < 1 or years > 10:
        return jsonify({"error": "Periode prediksi max 10 tahun"}), 400

    result = predict_energy_service(scenario, years)
    
    # Save prediction to database only if requested
    if save_to_db:
        try:
            # Save predictions only (for backward compatibility)
            save_prediction_history(scenario, years, result['predictions'])
        except Exception as e:
            print(f"Warning: Failed to save prediction history: {e}")


    return jsonify({
        "status": "success",
        "scenario": scenario,
        "years": years,
        "predictions": result['predictions'],  # Changed from 'prediction' to 'predictions'
        "lower_bounds": result['lower_bounds'],
        "upper_bounds": result['upper_bounds'],
       "last_actual_year": result['last_actual_year'],
       "last_actual_value": result['last_actual_value'],
        "saved_to_database": save_to_db
    })

def get_avg_gdp_growth():
    result = db.session.execute(text("""
        SELECT tahun, nilai FROM gdp ORDER BY tahun
    """)).fetchall()

    if len(result) < 2:
        return 0.05

    growth_rates = []

    for i in range(1, len(result)):
        prev = result[i-1].nilai
        curr = result[i].nilai

        if prev and prev != 0:
            growth = (curr - prev) / prev
            growth_rates.append(growth)

    return sum(growth_rates) / len(growth_rates)

# ===== DATA MANAGEMENT API ENDPOINTS =====

@api_bp.route("/data/fetch", methods=["POST"])
def fetch_data():
    """Fetch data dari API eksternal"""
    try:
        data = request.json
        data_type = data.get("dataType", "all")
        start_year = data.get("startYear", 1990)
        end_year = data.get("endYear", 2023)
        
        result = fetch_data_from_api(data_type, start_year, end_year)

        # --- PATCH: Rename 'entityname' to 'Entity' in energy data ---
        if result and 'energy_data' in result and isinstance(result['energy_data'], list):
            for row in result['energy_data']:
                if 'entityname' in row and 'Entity' not in row:
                    row['Entity'] = row.pop('entityname')
        # --- END PATCH ---

        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@api_bp.route("/data/upload", methods=["POST"])
def upload_data():
    """Upload data dari file CSV/Excel"""
    try:
        energy_file = request.files.get('energyFile')
        gdp_file = request.files.get('gdpFile')
        
        if not energy_file and not gdp_file:
            return jsonify({
                "success": False,
                "message": "Minimal satu file harus diupload"
            }), 400
        
        result = upload_data_from_files(energy_file, gdp_file)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@api_bp.route("/data/energy", methods=["GET"])
def energy_data():
    """Get preview data energi dari MySQL"""
    try:
        limit = request.args.get('limit', 10, type=int)
        data = get_energy_from_db()  # Returns list of dicts
        
        if not data or len(data) == 0:
            return jsonify({
                "success": True,
                "data": [],
                "count": 0,
                "message": "Belum ada data energy. Lakukan fetch/upload terlebih dahulu."
            })
        
        # Limit results (ambil data terakhir)
        data_limited = data[-limit:] if len(data) > limit else data
        
        # Convert Decimal to float for JSON serialization
        data_json = []
        for row in data_limited:
            data_json.append({
                "year": int(row.get('Year', 0)),
                "fossil_fuels__twh": float(row.get('fossil_fuels__twh', 0)),
                "energy_value": float(row.get('fossil_fuels__twh', 0)),  # Alias untuk frontend
                "updated_at": row.get('updated_at').isoformat() if row.get('updated_at') else None
            })
        
        return jsonify({
            "success": True,
            "data": data_json,
            "count": len(data_json)
        })
    except Exception as e:
        print(f"Error in energy_data API: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@api_bp.route("/data/gdp", methods=["GET"])
def gdp_data():
    """Get preview data GDP dari MySQL"""
    try:
        limit = request.args.get('limit', 10, type=int)
        data = get_gdp_from_db()  # Returns list of dicts
        
        if not data or len(data) == 0:
            return jsonify({
                "success": True,
                "data": [],
                "count": 0,
                "message": "Belum ada data GDP. Lakukan fetch/upload terlebih dahulu."
            })
        
        # Limit results (ambil data terakhir)
        data_limited = data[-limit:] if len(data) > limit else data
        
        # Convert Decimal to float for JSON serialization
        data_json = []
        for row in data_limited:
            data_json.append({
                "year": int(row.get('year', 0)),
                "gdp": float(row.get('gdp', 0)),
                "updated_at": row.get('updated_at').isoformat() if row.get('updated_at') else None
            })
        
        return jsonify({
            "success": True,
            "data": data_json,
            "count": len(data_json)
        })
    except Exception as e:
        print(f"Error in gdp_data API: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
    except Exception as e:
        print(f"Error in gdp_data API: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
    

@api_bp.route("/gdp/scenario", methods=["GET"])
def get_gdp_scenario():
    try:
        data = get_gdp_from_db()  # ambil dari function yang sama

        if not data or len(data) < 2:
            return jsonify({
                "success": False,
                "message": "Data tidak cukup untuk menghitung pertumbuhan"
            })

        # Urutkan berdasarkan tahun
        data_sorted = sorted(data, key=lambda x: x['year'])

        growth_rates = []

        for i in range(1, len(data_sorted)):
            prev = float(data_sorted[i-1]['gdp'])
            curr = float(data_sorted[i]['gdp'])

            if prev != 0:
                growth = ((curr - prev) / prev) * 100
                growth_rates.append(growth)

        if len(growth_rates) == 0:
            return jsonify({
                "success": False,
                "message": "Tidak ada growth rate yang valid"
            })

        avg_growth = sum(growth_rates) / len(growth_rates)

        return jsonify({
            "success": True,
            "baseline": round(avg_growth, 2),
            "moderate": round(avg_growth, 2),
            "optimistic": round(avg_growth + 2, 2),
            "pessimistic": round(avg_growth - 2, 2)
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@api_bp.route("/data/stats", methods=["GET"])
def data_stats():
    """Get statistik data dari MySQL"""
    try:
        stats = get_data_stats_from_db()
        return jsonify({
            "success": True,
            "stats": stats
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@api_bp.route("/data/progress/<task_id>", methods=["GET"])
def data_progress(task_id):
    """Monitor progress untuk operasi data (placeholder untuk future implementation)"""
    # Untuk saat ini, return completed status
    # Bisa dikembangkan dengan Celery atau background task manager
    return jsonify({
        "status": "completed",
        "progress": 100,
        "log": "Proses selesai"
    })


# ===== SCHEDULER ENDPOINTS - DISABLED =====
# Scheduler tidak reliable di environment lokal/development
# Untuk production, gunakan cron job atau cloud scheduler service

# @api_bp.route("/data/schedule", methods=["POST"])
# def save_schedule():
#     """Save jadwal scraping otomatis"""
#     ...

# @api_bp.route("/data/schedule", methods=["GET"])
# def get_schedule():
#     """Get status jadwal scraping otomatis"""
#     ...


@api_bp.route("/data/validate", methods=["GET"])
def validate_data():
    """Validasi kompatibilitas data untuk training model"""
    try:
        validation = validate_data_compatibility()
        return jsonify(validation)
        
    except Exception as e:
        return jsonify({
            "valid": False,
            "message": str(e)
        }), 500


@api_bp.route("/data/alignment-report", methods=["GET"])
def alignment_report():
    """Get detailed alignment report"""
    try:
        report = get_data_alignment_report()
        return jsonify(report)
        
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


# ===== MODEL TRAINING API ENDPOINTS =====

@api_bp.route("/model/train", methods=["POST"])
def train_model():
    """Retrain ARIMAX model dengan data terbaru"""
    try:
        # Get configuration from request
        data = request.json or {}
        train_test_split = data.get('trainTestSplit', 80) / 100  # Convert percentage to decimal
        forecast_years = data.get('forecastYears', 3)  # Number of years to forecast
        order_mode = data.get('orderMode', 'auto')  # 'auto' or 'manual'
        manual_order = None
        
        # Validasi range
        if train_test_split < 0.5 or train_test_split > 0.95:
            return jsonify({
                "success": False,
                "message": "Train/test split harus antara 50% - 95%"
            }), 400
        
        # Get manual order if specified
        if order_mode == 'manual':
            order_data = data.get('order', {})
            p = order_data.get('p', 3)
            d = order_data.get('d', 2)
            q = order_data.get('q', 6)
            manual_order = (p, d, q)
            print(f"API received manual order: p={p}, d={d}, q={q} -> {manual_order}")
        
        print(f"Training with mode={order_mode}, manual_order={manual_order}, forecast_years={forecast_years}")
        
        # Call train_service untuk retrain model
        result = retrain_model(
            train_test_split=train_test_split,
            order_mode=order_mode,
            manual_order=manual_order,
            forecast_years=forecast_years
        )
        
        if result["status"] == "success":
            return jsonify({
                "success": True,
                "message": result["message"],
                "taskId": "training_complete",
                "details": {
                    "rows_used": result.get("rows_used"),
                    "year_range": result.get("year_range"),
                    "energy_stats": result.get("energy_stats"),
                    "gdp_stats": result.get("gdp_stats")
                },
                "metrics": result.get("metrics", {})
            })
        else:
            return jsonify({
                "success": False,
                "message": result["message"],
                "details": result.get("details")
            }), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error training model: {str(e)}"
        }), 500
@api_bp.route("/model/training-progress/<task_id>", methods=["GET"])
def training_progress(task_id):
    """Monitor progress training (simplified untuk saat ini)"""
    # Untuk implementasi sederhana, langsung return completed
    # Bisa dikembangkan dengan websocket atau polling yang lebih advanced
    return jsonify({
        "status": "completed",
        "currentStep": 5,
        "overallProgress": 100,
        "message": "Training selesai!"
    })


@api_bp.route("/model/info", methods=["GET"])
def model_info():
    """Get info model saat ini dari active model di database"""
    import os
    from datetime import datetime
    import joblib
    
    try:
        # Try to get active model from database first
        from services.database_service import get_active_model
        active_model = get_active_model()
        
        if active_model:
            # Use active model from database
            last_trained = active_model['training_date'].strftime("%d %b %Y %H:%M")
            
            return jsonify({
                "success": True,
                "version": "ARIMAX v1.0",
                "mape": float(active_model['mape']),
                "lastTrained": last_trained,
                "dataCount": active_model['total_data'],
                "trainSize": active_model.get('train_size'),
                "testSize": active_model.get('test_size'),
                "trainPercentage": active_model.get('train_percentage'),
                "testPercentage": active_model.get('test_percentage'),
                "forecastYears": active_model.get('forecast_years', 3)
            })
        
        # Fallback: Load from file if no active model in database
        model_path = "models/arimax_model.pkl"
        metrics_path = "models/model_metrics.pkl"
        
        if os.path.exists(model_path):
            # Get file modification time
            mtime = os.path.getmtime(model_path)
            last_trained = datetime.fromtimestamp(mtime).strftime("%d %b %Y %H:%M")
            
            # Get data count from CSV
            import pandas as pd
            energy_path = "data/raw/energy.csv"
            data_count = 0
            
            if os.path.exists(energy_path):
                df = pd.read_csv(energy_path)
                data_count = len(df)
            
            # Load metrics if available
            mape = None
            if os.path.exists(metrics_path):
                metrics = joblib.load(metrics_path)
                mape = metrics.get("mape")
            
            return jsonify({
                "success": True,
                "version": "ARIMAX v1.0",
                "mape": mape,
                "lastTrained": last_trained,
                "dataCount": data_count
            })
        else:
            return jsonify({
                "success": True,
                "version": "ARIMAX v1.0",
                "mape": None,
                "lastTrained": "-",
                "dataCount": 0
            })
            
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@api_bp.route("/model/metrics", methods=["GET"])
def model_metrics():
    """Get active model metrics dari database"""
    try:
        from services.database_service import get_db_connection
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get active model metrics
        query = """
        SELECT model_version, mape, forecast_years, training_date, p, d, q
        FROM training_history
        WHERE model_status = 'active'
        ORDER BY training_date DESC
        LIMIT 1
        """
        
        cursor.execute(query)
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if result:
            mape = float(result['mape'])
            accuracy = round(100 - mape, 2)
            
            return jsonify({
                "success": True,
                "metrics": {
                    "model_version": result['model_version'],
                    "order": f"({result['p']},{result['d']},{result['q']})",
                    "mape": mape,
                    "accuracy": accuracy,
                    "forecast_years": result['forecast_years'],
                    "training_date": result['training_date'].strftime("%Y-%m-%d") if result['training_date'] else None
                }
            })
        else:
            return jsonify({
                "success": False,
                "message": "No active model found"
            }), 404
            
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@api_bp.route("/model/parameters", methods=["GET"])
def model_parameters():
    """Get model parameters dari saved model"""
    import os
    import joblib
    
    try:
        metrics_path = "models/model_metrics.pkl"
        
        if os.path.exists(metrics_path):
            metrics = joblib.load(metrics_path)
            return jsonify({
                "success": True,
                "parameters": {
                    "order": metrics.get("order", "(3,2,6)"),
                    "p": metrics.get("p", 3),
                    "d": metrics.get("d", 2),
                    "q": metrics.get("q", 6)
                },
                "metrics": {
                    "mae": metrics.get("mae"),
                    "rmse": metrics.get("rmse"),
                    "mape": metrics.get("mape"),
                    "r2": metrics.get("r2")
                },
                "training": {
                    "train_size": metrics.get("train_size", 0),
                    "test_size": metrics.get("test_size", 0)
                }
            })
        else:
            return jsonify({
                "success": False,
                "message": "Model belum di-training"
            }), 404
            
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# ===== HISTORY API ENDPOINTS =====

@api_bp.route("/history/training", methods=["GET"])
def history_training():
    """Get training history dari database"""
    try:
        limit = request.args.get('limit', 50, type=int)
        history = get_training_history(limit)
        
        return jsonify({
            "success": True,
            "data": history
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@api_bp.route("/training-history/<int:id>", methods=["GET"])
def get_training_detail(id):
    """Get detail training history by ID with visualization plots"""
    try:
        from services.database_service import get_db_connection
        import json
        
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT * FROM training_history WHERE id = %s
        """, (id,))
        
        record = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        if record:
            # Convert datetime to string
            if record.get('training_date'):
                record['training_date'] = record['training_date'].isoformat()
            if record.get('created_at'):
                record['created_at'] = record['created_at'].isoformat()
            
            # Parse preprocessing_steps JSON if exists
            if record.get('preprocessing_steps'):
                try:
                    record['preprocessing_steps'] = json.loads(record['preprocessing_steps'])
                except:
                    record['preprocessing_steps'] = None
            
            return jsonify(record)
        else:
            return jsonify({"error": "Training history not found"}), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/history/data-update", methods=["GET"])
def history_data_update():
    """Get data update history dari database"""
    try:
        limit = request.args.get('limit', 50, type=int)
        history = get_data_update_history(limit)
        
        return jsonify({
            "success": True,
            "data": history
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@api_bp.route("/history/prediction", methods=["GET"])
def history_prediction():
    """Get prediction history dari database"""
    try:
        limit = request.args.get('limit', 50, type=int)
        history = get_prediction_history(limit)
        
        return jsonify({
            "success": True,
            "data": history
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@api_bp.route("/prediction/latest", methods=["GET"])
def get_latest_prediction():
    """Get latest prediction from database (auto-updated by dashboard)"""
    try:
        from services.database_service import get_db_connection
        from services.data_mysql_service import get_energy_from_db
        import pandas as pd
        import json
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'predictions': [], 'years': 0, 'scenario': 'moderat'})
        
        cursor = connection.cursor(dictionary=True)
        
        # Get latest moderat prediction from database
        cursor.execute("""
                       SELECT p.*
                       FROM prediction_history p
                       JOIN training_history t
                       ON p.model_id = t.id
                       WHERE t.model_status = 'active'
                       ORDER BY p.prediction_date DESC
                       LIMIT 1;

        """)
        
        record = cursor.fetchone()
        cursor.close()
        connection.close()
        
        # If no record, try to generate prediction automatically
        if not record:
            print("No prediction record found, generating default prediction...")
            try:
                # Get active model's forecast_years
                active_model = get_active_model()
                forecast_years = active_model.get('forecast_years', 3) if active_model else 3
                
                # Generate prediction
                forecast_result = predict_energy_service(scenario='moderat', years=forecast_years)
                
                # Save to database
                model_version = f"ARIMAX ({active_model.get('p', 0)},{active_model.get('d', 0)},{active_model.get('q', 0)})" if active_model else 'ARIMAX v1.0'
                prediction_values = forecast_result['predictions']
                
                save_prediction_history(
                    scenario='moderat',
                    years=forecast_years,
                    prediction_data=prediction_values,
                    model_version=model_version
                )
                
                # Get last year
                energy_data = get_energy_from_db()
                if energy_data:
                    energy_df = pd.DataFrame(energy_data)
                    last_year = int(energy_df['Year'].max())
                else:
                    last_year = 2024
                
                # Format predictions
                formatted_predictions = []
                for i, value in enumerate(prediction_values):
                    formatted_predictions.append({
                        'year': last_year + i + 1,
                        'prediction_value': float(value)
                    })
                
                return jsonify({
                    'predictions': formatted_predictions,
                    'years': forecast_years,
                    'scenario': 'moderat'
                })
                
            except Exception as gen_error:
                print(f"Error generating prediction: {gen_error}")
                return jsonify({'predictions': [], 'years': 0, 'scenario': 'moderat'})
        
        # Get last year from energy data
        energy_data = get_energy_from_db()
        if energy_data:
            energy_df = pd.DataFrame(energy_data)
            last_year = int(energy_df['Year'].max())
        else:
            last_year = 2024
        
        # Parse prediction_data
        prediction_values = json.loads(record['prediction_data']) if record['prediction_data'] else []
        
        # Format predictions starting from last_year + 1
        formatted_predictions = []
        for i, value in enumerate(prediction_values):
            formatted_predictions.append({
                'year': last_year + i + 1,
                'prediction_value': float(value)
            })
        
        return jsonify({
            'predictions': formatted_predictions,
            'years': record['years'],
            'scenario': record['scenario']
        })
        
    except Exception as e:
        print(f"Error getting latest prediction: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'predictions': [],
            'years': 0,
            'scenario': 'moderat'
        }), 500


@api_bp.route("/data/range", methods=["GET"])
def get_data_range():
    try:
        from services.database_service import get_db_connection
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT 
            MIN(year) AS min_year,
            MAX(year) AS max_year,
            COUNT(*) AS total_records
        FROM energy_data
        """

        cursor.execute(query)
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "min_year": result["min_year"],
            "max_year": result["max_year"],
            "total_records": result["total_records"]
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@api_bp.route("/history/summary", methods=["GET"])
def history_summary():
    """Get summary statistics untuk dashboard riwayat"""
    try:
        summary = get_history_summary()
        
        return jsonify({
            "success": True,
            "data": summary
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@api_bp.route("/history/clear", methods=["DELETE"])
def clear_history():
    """Clear all history data"""
    try:
        success = clear_all_history()
        
        if success:
            return jsonify({
                "success": True,
                "message": "Semua riwayat berhasil dihapus"
            })
        else:
            return jsonify({
                "success": False,
                "message": "Gagal menghapus riwayat"
            }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# ===== MODEL STAGING SYSTEM API =====

@api_bp.route("/model/active", methods=["GET"])
def get_active_model_info():
    """Get currently active model"""
    try:
        model = get_active_model()
        
        if model:
            return jsonify({
                "success": True,
                "model": model
            })
        else:
            return jsonify({
                "success": False,
                "message": "Tidak ada model aktif"
            })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@api_bp.route("/model/candidates", methods=["GET"])
def get_candidate_models_list():
    """Get all candidate models"""
    try:
        candidates = get_candidate_models()
        
        return jsonify({
            "success": True,
            "candidates": candidates
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@api_bp.route("/model/comparison", methods=["GET"])
def get_models_comparison():
    """Get all models (active + candidates) for comparison"""
    try:
        models = get_all_models_comparison()
        
        # Convert Decimal and datetime to JSON-serializable formats
        serialized_models = []
        for model in models:
            serialized_model = {}
            for key, value in model.items():
                if isinstance(value, Decimal):
                    serialized_model[key] = float(value)
                elif isinstance(value, datetime):
                    serialized_model[key] = value.isoformat()
                else:
                    serialized_model[key] = value
            serialized_models.append(serialized_model)
        
        return jsonify({
            "success": True,
            "models": serialized_models
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@api_bp.route("/model/activate/<int:model_id>", methods=["POST"])
def activate_model_endpoint(model_id):
    """Activate a candidate model"""
    try:
        data = request.json or {}
        activated_by = data.get('activated_by', 'admin')
        
        success = activate_model(model_id, activated_by)
        
        if success:
            return jsonify({
                "success": True,
                "message": f"Model ID {model_id} berhasil diaktifkan"
            })
        else:
            return jsonify({
                "success": False,
                "message": "Gagal mengaktifkan model"
            }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@api_bp.route("/model/delete/<int:model_id>", methods=["DELETE"])
def delete_model_endpoint(model_id):
    """Delete a candidate model"""
    try:
        success = delete_candidate_model(model_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": f"Model ID {model_id} berhasil dihapus"
            })
        else:
            return jsonify({
                "success": False,
                "message": "Gagal menghapus model (mungkin model sudah aktif)"
            }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# ============= DASHBOARD API ENDPOINTS ===============
@api_bp.route("/dashboard/model-info", methods=["GET"])
def dashboard_model_info():
    """Get active model info for dashboard"""
    try:
        import pandas as pd
        import numpy as np
        import os
        import pickle
        
        active_model = get_active_model()
        
        if not active_model:
            return jsonify({
                "success": False,
                "model_version": "No Active Model",
                "mape": None,
                "p": None,
                "d": None,
                "q": None,
                "training_date": None
            })
        
        # Get p, d, q from database
        p = active_model.get('p', 0)
        d = active_model.get('d', 0)
        q = active_model.get('q', 0)
        order_str = f"({p},{d},{q})"
        
        # Convert Decimal and datetime for JSON
        mape_value = float(active_model['mape']) if active_model.get('mape') else None
        training_date = active_model['training_date'].isoformat() if active_model.get('training_date') else None
        activated_at = active_model['activated_at'].isoformat() if active_model.get('activated_at') else None
        
        # Load model file to get test data if available
        test_data = None
        error_data = None
        
        try:
            model_path = os.path.join('models', 'arimax_model.pkl')
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    model_info = pickle.load(f)
                    
                # Generate test data for comparison chart
                if isinstance(model_info, dict) and 'y_test' in model_info and 'y_pred' in model_info:
                    y_test = model_info['y_test']
                    y_pred = model_info['y_pred']
                    
                    # Get test years from model
                    if 'test_years' in model_info:
                        test_years = model_info['test_years']
                    else:
                        # Fallback: assume last 5 years of training data
                        energy_data = get_energy_from_db()
                        if energy_data:
                            energy_df = pd.DataFrame(energy_data)
                            all_years = sorted(energy_df['Year'].unique())
                            test_years = all_years[-len(y_test):]
                        else:
                            test_years = list(range(2020, 2020 + len(y_test)))
                    
                    test_data = {
                        'years': [str(int(year)) for year in test_years],
                        'actual': [float(val) for val in y_test],
                        'predicted': [float(val) for val in y_pred]
                    }
                    
                    # Calculate errors for error distribution chart
                    errors = ((y_pred - y_test) / y_test * 100)  # Percentage errors
                    
                    # Create bins for error distribution
                    bins = [-10, -5, -2, 0, 2, 5, 10]
                    bin_labels = ['< -5%', '-5% to -2%', '-2% to 0%', '0% to 2%', '2% to 5%', '> 5%']
                    hist, _ = np.histogram(errors, bins=bins)
                    
                    error_data = {
                        'bins': bin_labels,
                        'frequencies': [int(x) for x in hist]
                    }
                else:
                    # Model in old format - generate test data from historical data
                    print("Model in old format, generating test data from historical data...")
                    
                    energy_data = get_energy_from_db()
                    if energy_data:
                        energy_df = pd.DataFrame(energy_data)
                        
                        # Get metrics to determine test split
                        metrics_path = os.path.join('models', 'model_metrics.pkl')
                        if os.path.exists(metrics_path):
                            import joblib as jl
                            metrics = jl.load(metrics_path)
                            test_size = metrics.get('test_size', 12)  # Default 12
                            
                            # Get last test_size years as test data
                            all_data = energy_df.sort_values('Year')
                            test_df = all_data.tail(test_size)
                            
                            # Extract model from old format
                            if isinstance(model_info, dict) and 'model' in model_info:
                                model_obj = model_info['model']
                            else:
                                model_obj = model_info
                            
                            # Try to generate predictions for test set
                            try:
                                # Get GDP data for exogenous variables
                                gdp_data = get_gdp_from_db()
                                if gdp_data:
                                    gdp_df = pd.DataFrame(gdp_data)
                                    
                                    # Align test years with GDP
                                    test_years = test_df['Year'].values
                                    test_gdp = gdp_df[gdp_df['year'].isin(test_years)].sort_values('year')
                                    
                                    if len(test_gdp) == len(test_df):
                                        # Make predictions
                                        exog_test = test_gdp[['gdp']]
                                        predictions = model_obj.forecast(steps=len(test_df), exog=exog_test)
                                        
                                        # Create test data
                                        test_data = {
                                            'years': [str(int(year)) for year in test_years],
                                            'actual': [float(val) for val in test_df['fossil_fuels__twh'].values],
                                            'predicted': [float(val) for val in predictions]
                                        }
                                        
                                        # Calculate errors
                                        actual_vals = test_df['fossil_fuels__twh'].values
                                        errors = ((predictions - actual_vals) / actual_vals * 100)
                                        
                                        bins = [-10, -5, -2, 0, 2, 5, 10]
                                        bin_labels = ['< -5%', '-5% to -2%', '-2% to 0%', '0% to 2%', '2% to 5%', '> 5%']
                                        hist, _ = np.histogram(errors, bins=bins)
                                        
                                        error_data = {
                                            'bins': bin_labels,
                                            'frequencies': [int(x) for x in hist]
                                        }
                                        
                                        print("✓ Generated test data successfully from old model")
                            except Exception as e:
                                print(f"Could not generate predictions from old model: {e}")
        except Exception as e:
            print(f"Could not load model test data: {e}")
            import traceback
            traceback.print_exc()
        
        # Get training duration from database
        duration = "-"
        if 'training_duration' in active_model and active_model['training_duration'] is not None:
            duration = f"{float(active_model['training_duration']):.2f}s"
        
        response_data = {
            "success": True,
            "model_version": f"ARIMAX {order_str}",
            "mape": mape_value,
            "r2": float(active_model['r2']) if active_model.get('r2') else None,
            "rmse": float(active_model['rmse']) if active_model.get('rmse') else None,
            "mae": float(active_model['mae']) if active_model.get('mae') else None,
            "p": p,
            "d": d,
            "q": q,
            "order": order_str,
            "params": order_str,
            "training_date": training_date,
            "lastTrained": training_date,
            "duration": duration,
            "activated_at": activated_at,
            "activated_by": active_model.get('activated_by', 'system')
        }
        
        # Add test data if available
        if test_data:
            response_data['testData'] = test_data
        if error_data:
            response_data['errorData'] = error_data
            
        return jsonify(response_data)
    except Exception as e:
        import traceback
        print(f"Error in dashboard_model_info: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@api_bp.route("/dashboard/prediction", methods=["GET"])
def dashboard_prediction():
    """Get prediction data for dashboard chart (2024-2030)"""
    try:
        import pandas as pd
        import os
        
        # Get historical data
        energy_data = get_energy_from_db()
        gdp_data = get_gdp_from_db()
        
        # Calculate aligned records (common years only)
        aligned_count = 0
        data_range = {"start": None, "end": None}
        
        if energy_data and gdp_data:
            energy_df = pd.DataFrame(energy_data)
            gdp_df = pd.DataFrame(gdp_data)
            
            # Find common years (intersection)
            energy_years = set(energy_df['Year'].unique())
            gdp_years = set(gdp_df['year'].unique())
            common_years = sorted(energy_years.intersection(gdp_years))
            
            aligned_count = len(common_years)
            if common_years:
                data_range = {
                    "start": int(min(common_years)),
                    "end": int(max(common_years))
                }
        
        if not energy_data or not gdp_data:
            # Return stats even if prediction fails
            return jsonify({
                "success": False,
                "error": "Data tidak tersedia. Silakan upload data terlebih dahulu.",
                "total_records": aligned_count,
                "data_range": data_range
            }), 400
        
        # Get forecast years from active model (default to 3 if not set)
        active_model = get_active_model()
        forecast_years = active_model.get('forecast_years', 3) if active_model else 3
        
        print(f"Dashboard: Using forecast_years = {forecast_years} from active model")
        
        # Get predictions using forecast_years from model
        try:
            forecast_result = predict_energy_service(scenario='moderat', years=forecast_years)
            
            # Convert forecast dict to predictions format with confidence intervals
            energy_df = pd.DataFrame(energy_data)
            last_year = int(energy_df['Year'].max())
            
            predictions = [
                {
                    "year": last_year + i + 1, 
                    "value": float(forecast_result['predictions'][i]),
                    "lowerBound": float(forecast_result['lower_bounds'][i]),
                    "upperBound": float(forecast_result['upper_bounds'][i])
                } 
                for i in range(len(forecast_result['predictions']))
            ]
        except Exception as e:
            # Return data stats even if prediction fails
            print(f"Prediction error: {e}")
            return jsonify({
                "success": False,
                "error": f"Gagal membuat prediksi: {str(e)}",
                "total_records": aligned_count,
                "data_range": data_range
            }), 400
        
        # Get ALL historical data (not just last 15 years)
        energy_df = pd.DataFrame(energy_data)
        
        # Format ALL historical data for chart
        all_historical = [
            {
                "year": int(row['Year']),
                "value": float(row['fossil_fuels__twh'])
            }
            for _, row in energy_df.iterrows()
        ]
        
        # Calculate trend (average yearly change)
        if len(energy_df) >= 2:
            recent_years = energy_df.tail(10)
            trend = recent_years['fossil_fuels__twh'].diff().mean()
        else:
            trend = 0
        
        # Get prediction for 2030
        prediction_2030 = next((p['value'] for p in predictions if p['year'] == 2030), None)
        
        # Auto-save prediction to database for landing page
        try:
            active_model = get_active_model()
            model_version = f"ARIMAX ({active_model.get('p', 0)},{active_model.get('d', 0)},{active_model.get('q', 0)})" if active_model else 'ARIMAX v1.0'
            
            # Save only prediction values (not full object)
            prediction_values = [p['value'] for p in predictions]
            save_prediction_history(
                scenario='moderat',
                years=forecast_years,
                prediction_data=prediction_values,
                model_version=model_version
            )
            print(f"✓ Saved {forecast_years} years prediction to database")
        except Exception as save_error:
            print(f"Warning: Failed to save prediction history: {save_error}")
        
        return jsonify({
            "success": True,
            "historical": all_historical,
            "predictions": predictions,
            "prediction_2030": prediction_2030,
            "trend": float(trend) if trend else 0,
            "total_records": aligned_count,
            "data_range": data_range,
            "last_actual_year": last_year,
"last_actual_value": float(energy_df.loc[energy_df['Year'] == last_year, 'fossil_fuels__twh'].values[0]),

        })
    except Exception as e:
        import traceback
        print(f"Error in dashboard prediction: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@api_bp.route("/dashboard/recent-activities", methods=["GET"])
def get_recent_activities():
    """Get recent activities from all history tables"""
    try:
        activities = []
        
        # Get training history
        training_history = get_training_history(limit=5)
        for item in training_history:
            # Use training_date or created_at as timestamp
            timestamp = item.get('created_at') or item.get('training_date')
            if timestamp and isinstance(timestamp, str):
                # Already formatted as string, convert to datetime for isoformat
                from datetime import datetime as dt
                try:
                    timestamp_obj = dt.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                    timestamp = timestamp_obj.isoformat()
                except:
                    pass  # Keep as is if parsing fails
            elif timestamp:
                timestamp = timestamp.isoformat()
            else:
                timestamp = datetime.now().isoformat()
                
            activities.append({
                "type": "training",
                "title": f"Model Training - {item.get('model_version', 'ARIMAX')}",
                "description": f"MAPE: {item.get('mape', 0):.2f}% | R²: {item.get('r2', 0):.3f}",
                "timestamp": timestamp
            })
        
        # Get data update history
        data_history = get_data_update_history(limit=5)
        for item in data_history:
            # Use update_date or created_at as timestamp
            timestamp = item.get('created_at') or item.get('update_date')
            if timestamp and isinstance(timestamp, str):
                from datetime import datetime as dt
                try:
                    timestamp_obj = dt.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                    timestamp = timestamp_obj.isoformat()
                except:
                    pass
            elif timestamp:
                timestamp = timestamp.isoformat()
            else:
                timestamp = datetime.now().isoformat()
                
            activities.append({
                "type": "data",
                "title": f"Data Update - {item.get('update_type', 'All').replace('_', ' ').title()}",
                "description": f"{item.get('records_updated', 0)} records processed",
                "timestamp": timestamp
            })
        
        # Get prediction history
        prediction_history = get_prediction_history(limit=5)
        for item in prediction_history:
            # Use prediction_date or created_at as timestamp
            timestamp = item.get('created_at') or item.get('prediction_date')
            if timestamp and isinstance(timestamp, str):
                from datetime import datetime as dt
                try:
                    timestamp_obj = dt.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                    timestamp = timestamp_obj.isoformat()
                except:
                    pass
            elif timestamp:
                timestamp = timestamp.isoformat()
            else:
                timestamp = datetime.now().isoformat()
                
            activities.append({
                "type": "prediction",
                "title": f"Prediction - {item.get('scenario', 'Unknown').capitalize()}",
                "description": f"Prediksi {item.get('years', 0)} tahun ke depan",
                "timestamp": timestamp
            })
        
        # Sort by timestamp (newest first)
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({
            "success": True,
            "activities": activities[:10]  # Return top 10
        })
    except Exception as e:
        print(f"Error getting recent activities: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "activities": [],
            "error": str(e)
        }), 500


@api_bp.route("/dashboard/system-status", methods=["GET"])
def get_system_status():
    """Get system status information"""
    try:
        import time
        from datetime import timedelta
        from services.database_service import get_db_connection
        
        # Calculate uptime (simplified - use process start time in production)
        uptime_seconds = int(time.time() % 86400)  # Reset daily for demo
        uptime = str(timedelta(seconds=uptime_seconds)).split('.')[0]
        
        # Check database connection (REAL CHECK)
        database_connected = False
        try:
            conn = get_db_connection()
            if conn:
                database_connected = True
                conn.close()
        except:
            database_connected = False
        
        # Check if model exists
        model_exists = False
        model_running = False
        try:
            import os
            model_path = os.path.join('models', 'arimax_model.pkl')
            if os.path.exists(model_path):
                model_exists = True
                # If database is connected and model exists, consider it running
                model_running = database_connected and model_exists
        except:
            pass
        
        return jsonify({
            "success": True,
            "uptime": uptime,
            "modelServerRunning": model_running,
            "databaseConnected": database_connected
        })
    except Exception as e:
        print(f"Error getting system status: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500