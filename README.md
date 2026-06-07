# OpsDesk360

OpsDesk360 is a modular, multi‑tenant SaaS application for small and medium businesses. It provides inventory management, point of sale (POS), customer management, employee commissions, appointments, and more – all with bilingual support (English/Arabic) and offline‑capable POS.

## Tech Stack

- **Backend:** Django (Python)
- **Frontend:** Tailwind CSS, HTMX, Alpine.js
- **Database:** PostgreSQL (separate database per client)
- **Deployment:** Any VPS (e.g., DigitalOcean, Oracle Cloud) with nginx + gunicorn
- **PWA:** Installable as a native app on desktop and mobile

## Features (Modular Add‑ons)

- Core: User management, dashboard, categories, items, customers
- POS with offline queue (localStorage)
- Inventory & stock tracking
- Appointments & calendar
- Employee commissions
- Loyalty program
- Medical records (add‑on)
- Super admin panel (client management, feature toggles, payments, support tickets)
- Bilingual (English/Arabic) with RTL support

## Setup for Development

1. **Clone the repository**  
   ```bash
   git clone https://github.com/AhmedDig/OpsDesk360.git
   cd OpsDesk360
