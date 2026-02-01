document.addEventListener("DOMContentLoaded", function () {
    const sidebarToggle = document.getElementById("sidebarToggle");
    const mobileMenuToggle = document.getElementById("mobileMenuToggle");
    const sidebar = document.querySelector(".sidebar");
    const overlay = document.getElementById("sidebarOverlay");

    // ==============================
    // Helper Functions
    // ==============================
    function toggleSidebar() {
        if (!sidebar) return;

        if (window.innerWidth <= 768) {
            sidebar.classList.toggle("active");
            if (overlay) overlay.classList.toggle("active");
        } else {
            // Desktop behavior
            if (sidebar.classList.contains("temp-expanded")) {
                sidebar.classList.remove("temp-expanded");
                sidebar.classList.add("collapsed");
            } else {
                sidebar.classList.toggle("collapsed");
            }
        }
    }

    function temporaryExpand() {
        if (
            sidebar &&
            sidebar.classList.contains("collapsed") &&
            window.innerWidth > 768
        ) {
            sidebar.classList.add("temp-expanded");
            sidebar.classList.remove("collapsed");
        }
    }

    function closeIfClickedOutside(e) {
        if (
            sidebar &&
            sidebar.classList.contains("temp-expanded") &&
            window.innerWidth > 768 &&
            !sidebar.contains(e.target)
        ) {
            collapseSidebarAndSubmenu();
        }
    }

    function collapseSidebarAndSubmenu() {
        sidebar.classList.remove("temp-expanded");
        sidebar.classList.add("collapsed");

        const cutiSubmenu = document.getElementById("cutiSubmenu");
        if (cutiSubmenu && cutiSubmenu.classList.contains("show")) {
            try {
                new bootstrap.Collapse(cutiSubmenu, { hide: true });
            } catch {
                cutiSubmenu.classList.remove("show");
            }
        }
    }


    // ==============================
    // Sidebar Toggle Events
    // ==============================

    // Use ID selectors for specific buttons to avoid duplication
    if (sidebarToggle) {
        sidebarToggle.addEventListener("click", (e) => {
            e.preventDefault();
            toggleSidebar();
        });
    }

    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener("click", (e) => {
            e.preventDefault();
            toggleSidebar();
        });
    }

    // Only add event listeners to sidebar-toggle elements that don't have IDs
    document
        .querySelectorAll(
            ".sidebar-toggle:not(#sidebarToggle):not(#mobileMenuToggle)"
        )
        .forEach((button) => {
            button.addEventListener("click", (e) => {
                e.preventDefault();
                toggleSidebar();
            });
        });

    // ==============================
    // Cuti Dropdown
    // ==============================
    let cutiLink =
        document.querySelector(
            'a[data-bs-toggle="collapse"][href="#cutiSubmenu"]'
        ) ||
        document.querySelector('.nav-link[href="#cutiSubmenu"]') ||
        document.querySelector('a[href="#cutiSubmenu"]') ||
        (() => {
            const icon = document.querySelector(".nav-link .fa-calendar-alt");
            return icon ? icon.closest(".nav-link") : null;
        })();

    if (cutiLink) {
        cutiLink.addEventListener(
            "click",
            (e) => {
                if (
                    sidebar &&
                    sidebar.classList.contains("collapsed") &&
                    window.innerWidth > 768
                ) {
                    e.preventDefault();
                    e.stopPropagation();
                    temporaryExpand();

                    setTimeout(
                        () => {
                            const cutiSubmenu =
                                document.getElementById("cutiSubmenu");

                            if (cutiSubmenu) {
                                try {
                                    new bootstrap.Collapse(cutiSubmenu, {
                                        show: true,
                                    });
                                } catch {
                                    cutiSubmenu.classList.add("show");
                                }
                            }
                        },

                        350
                    );
                }
            },

            true
        );
    }

    document.addEventListener("click", closeIfClickedOutside);

    document.addEventListener("click", (e) => {
        if (
            sidebar &&
            sidebar.classList.contains("temp-expanded") &&
            window.innerWidth > 768 &&
            e.target.closest("#cutiSubmenu .nav-link")
        ) {
            setTimeout(collapseSidebarAndSubmenu, 200);
        }
    });

    document.addEventListener("click", (e) => {
        if (
            sidebar &&
            sidebar.classList.contains("temp-expanded") &&
            window.innerWidth > 768
        ) {
            const cutiLinkClicked =
                e.target.closest(
                    'a[data-bs-toggle="collapse"][href="#cutiSubmenu"]'
                ) ||
                e.target.closest('.nav-link[href="#cutiSubmenu"]') ||
                e.target.closest('a[href="#cutiSubmenu"]');

            if (cutiLinkClicked) {
                const cutiSubmenu = document.getElementById("cutiSubmenu");

                if (cutiSubmenu && cutiSubmenu.classList.contains("show")) {
                    setTimeout(
                        () => {
                            sidebar.classList.remove("temp-expanded");
                            sidebar.classList.add("collapsed");
                        },

                        300
                    );
                }
            }
        }
    });

    // ==============================
    // Mobile Overlay
    // ==============================
    if (overlay) {
        overlay.addEventListener("click", () => {
            if (window.innerWidth <= 768) {
                sidebar.classList.remove("active");
                overlay.classList.remove("active");
            }
        });
    }

    // ==============================
    // Tanggal Otomatis
    // ==============================
    $(document).ready(function () {
        const now = new Date();

        const options = {
            weekday: "long",
            year: "numeric",
            month: "long",
            day: "numeric",
        };

        const dateString = now.toLocaleDateString("id-ID", options);
        $("#currentDate").text(dateString);
    });



    // ==============================
    // Batas Upload File
    // ==============================
    document.addEventListener("DOMContentLoaded", function () {
        document.getElementById("ktp").addEventListener("change", function (e) {
            const file = e.target.files[0];

            if (file) {
                const allowedTypes = ["image/jpeg", "image/png", "image/jpg"];

                if (!allowedTypes.includes(file.type)) {
                    alert("KTP hanya boleh gambar (jpg, jpeg, png)");
                    e.target.value = "";
                } else if (file.size > 2 * 1024 * 1024) {
                    alert("Ukuran file KTP maksimal 2 MB");
                    e.target.value = "";
                }
            }
        });

        document
            .getElementById("npwp")
            .addEventListener("change", function (e) {
                const file = e.target.files[0];

                if (file) {
                    if (file.type !== "application/pdf") {
                        alert("Scan NPWP hanya boleh PDF");
                        e.target.value = "";
                    } else if (file.size > 5 * 1024 * 1024) {
                        alert("Ukuran file NPWP maksimal 5 MB");
                        e.target.value = "";
                    }
                }
            });

        document
            .getElementById("sk_kontrak")
            .addEventListener("change", function (e) {
                const file = e.target.files[0];

                if (file) {
                    if (file.type !== "application/pdf") {
                        alert("SK Kontrak hanya boleh PDF");
                        e.target.value = "";
                    } else if (file.size > 5 * 1024 * 1024) {
                        alert("Ukuran file SK Kontrak maksimal 5 MB");
                        e.target.value = "";
                    }
                }
            });
    });

    // ==============================
    // Alert Konfirmasi Submit
    // ==============================
    document.addEventListener("DOMContentLoaded", function () {
        const form = document.querySelector("form");

        if (form) {
            form.addEventListener("submit", function (e) {
                if (!confirm("Apakah Anda yakin ingin mengirim data?")) {
                    e.preventDefault();
                }
            });
        }
    });

    // ==============================
    // Handle Resize
    // ==============================
    window.addEventListener("resize", () => {
        if (window.innerWidth > 768) {
            sidebar.classList.remove("active");
            if (overlay) overlay.classList.remove("active");
        } else {
            sidebar.classList.remove("collapsed", "temp-expanded");
        }
    });

  
});
