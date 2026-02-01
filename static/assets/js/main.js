document.addEventListener("DOMContentLoaded", () => {
    console.log("JS loaded ✅");

    const btn = document.getElementById("refreshBtn");
    if (!btn) {
        console.error("refreshBtn tidak ditemukan");
        return;
    }

     function setText(id, text) {
        const el = document.getElementById(id);
        if (el) el.innerText = text;
    }

    btn.addEventListener("click", async () => {
        console.log("Refresh diklik");

      startLoading(true);

      setText("energy-status", "Updating...");
      setText("gdp-status", "Updating...");

        try {
            const res = await fetch("/update-data");
            const json = await res.json();

            console.log(json);

            document.getElementById("energyStatus").innerText = "Updated";
            document.getElementById("energyTime").innerText =
                new Date().toLocaleString();

            document.getElementById("gdpStatus").innerText = "Updated";
            document.getElementById("gdpTime").innerText =
                new Date().toLocaleString();

            alert("Data berhasil diperbarui");
        } catch (e) {
          console.error("ERROR UPDATE:", e);
          alert("Gagal update data: " + e.message);
        } finally {
        stopLoading();
      }


        btn.disabled = false;
        btn.innerText = "🔄 Refresh Data";
    });
});
