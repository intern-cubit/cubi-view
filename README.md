# Folder Structure
cubiview-desktop/
├── backend/
│   ├── activator.py
│   ├── api.py                # NEW: Python backend REST server 
│   ├── credentials.py
│   ├── get_systemID.py
│   ├── GUI_backend.py
│   ├── html_report.py
│   ├── main.py
│   ├── monitor_installs.py
│   ├── page1_func_part1.py
│   ├── page1_func_part2.py
│   ├── page1_func_part3.py
│   ├── page2_func_part1.py
│   ├── page2_func_part2.py
│   ├── page2_func_part3.py
│   ├── prevent_vpn.py
│   ├── shutdown_detection.py
│   ├── write_report.py
│   ├── smtp_credentials.txt
│   ├── activation.json
│   ├── user_ID.json
│   ├── version.txt
│   └── requirements.txt      # list python packages, yet to add
│
├── frontend/
│   ├── src/
│   │   ├── pages/            # React pages (login, dashboard, report, etc.)
│   │   ├── components/       # React components (sidebar, header, toggles)
│   │   ├── api/              # Axios/fetch helpers
│   │   └── App.js
│   ├── public/
│   ├── package.json
│   └── ... (React build)
│
├── electron-app/
│   ├── main.js               # Electron main process
│   ├── preload.js (optional)
│   └── package.json
│
├── assets/                   # images, icons, logos
├── dist/                     # Electron build output
├── build/                    # React production build output
└── README.md
