# URL Shortener - Cloud Native Application

A cloud-native URL shortener system deployed on **Google Cloud Platform (GCP)**.

It includes:
- A static frontend and Flask-based redirect API on **Google Kubernetes Engine (GKE)**
- A **Google Cloud Function** that generates and stores shortened URLs
- A **PostgreSQL database** hosted on **Compute Engine (VM)**

---

## ⚙️ Architecture Overview

```
+----------------+                        +-----------------------------+
|   Frontend     |<--------------------->|       Cloud Function        |
| (Kubernetes)   |        POST           | - Generates short URL       |
+----------------+                       | - Inserts into PostgreSQL   |
                                         +-----------------------------+
                                                      |
                                                      v
                                         +-----------------------------+
                                         | PostgreSQL (Compute Engine)|
                                         | - Stores code + long URL   |
                                         +-----------------------------+
                                                      ^
+----------------+           GET                     |
|  Redirect API  |<----------------------------------+
|  (Kubernetes)  | - Resolves code                   |
|                | - Redirects to long URL           |
+----------------+
```

---

## ✅ Getting Started

### Prerequisites

- GCP account with billing enabled  
- `gcloud`, `kubectl`, and Docker installed  
- PostgreSQL CLI tools  
- Python 3 with `Flask`, `psycopg2-binary`, and `locust` packages  

---

## ☁️ Step 1: PostgreSQL on Compute Engine (VM)

```bash
# Create VM instance
gcloud compute instances create url-postgres-vm \
  --zone=us-central1-a \
  --machine-type=e2-standard-2 \
  --image-family=debian-11 \
  --image-project=debian-cloud \
  --tags=postgres \
  --boot-disk-size=10GB

# Allow external access to Postgres
gcloud compute firewall-rules create allow-postgres \
  --allow=tcp:5432 \
  --target-tags=postgres \
  --source-ranges=0.0.0.0/0

# SSH into the instance and run:
sudo apt update
sudo apt install postgresql postgresql-contrib

# Create DB and user
sudo -u postgres psql
CREATE DATABASE url_shortener;
CREATE USER url_user WITH ENCRYPTED PASSWORD 'url_pass';
GRANT ALL PRIVILEGES ON DATABASE url_shortener TO url_user;
\q

# Edit configuration for remote access
sudo nano /etc/postgresql/12/main/postgresql.conf
# Set: listen_addresses = '*'

sudo nano /etc/postgresql/12/main/pg_hba.conf
# Add line: host all all 0.0.0.0/0 md5

# Restart PostgreSQL
sudo systemctl restart postgresql
```

---

## ☸️ Step 2: Kubernetes Backend & Frontend

**deployment.yaml**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: url-shortener
spec:
  replicas: 2
  selector:
    matchLabels:
      app: url-shortener
  template:
    metadata:
      labels:
        app: url-shortener
    spec:
      containers:
        - name: url-shortener
          image: gcr.io/YOUR_PROJECT_ID/url-shortener:latest
          ports:
            - containerPort: 5000
          env:
            - name: DB_HOST
              value: "YOUR_VM_EXTERNAL_IP"
            - name: DB_PORT
              value: "5432"
            - name: DB_NAME
              value: "url_shortener"
            - name: DB_USER
              value: "url_user"
            - name: DB_PASSWORD
              value: "url_pass"
          readinessProbe:
            httpGet:
              path: /health
              port: 5000
            initialDelaySeconds: 5
            periodSeconds: 10
          resources:
            requests:
              cpu: "50m"
              memory: "128Mi"
            limits:
              cpu: "250m"
              memory: "256Mi"
```

**service.yaml**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: url-shortener-service
spec:
  selector:
    app: url-shortener
  ports:
    - protocol: TCP
      port: 80
      targetPort: 5000
  type: LoadBalancer
```

**Apply configuration:**

```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

**Enable Horizontal Pod Autoscaler:**

```bash
kubectl autoscale deployment url-shortener --cpu-percent=30 --min=2 --max=6
```

---

## 🧠 Step 3: Google Cloud Function - Shortener

**main.py**

```python
import os
import psycopg2
import string
import random
from flask import escape, jsonify, request

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

REDIRECT_BASE_URL = "http://YOUR_K8S_IP/redirect?code="

def generate_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def shorten_url(request):
    try:
        data = request.get_json()
        long_url = data.get("url")

        if not long_url:
            return jsonify({"error": "Missing 'url'"}), 400

        code = generate_code()

        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO urls (code, original_url)
            VALUES (%s, %s)
            ON CONFLICT (code) DO NOTHING;
        """, (code, long_url))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"short_url": REDIRECT_BASE_URL + escape(code)}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

**Deploy the function:**

```bash
gcloud functions deploy shorten-url \
  --runtime python310 \
  --trigger-http \
  --entry-point shorten_url \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DB_HOST=...,DB_PORT=5432,DB_NAME=url_shortener,DB_USER=url_user,DB_PASSWORD=url_pass
```

---

## 📊 Step 4: Load Testing with Locust

**locustfile.py**

```python
from locust import HttpUser, task, between
import random

class UrlShortenerUser(HttpUser):
    wait_time = between(1, 3)
    host = "https://YOUR_CLOUD_FUNCTION_URL"

    @task(2)
    def shorten_url(self):
        url = f"https://example.com/page{random.randint(1,10000)}"
        self.client.post("/", json={"url": url})

    @task(1)
    def redirect(self):
        self.client.get("http://YOUR_K8S_IP/redirect?code=test123", name="/redirect")
```

**Run:**

```bash
locust -f locustfile.py
```

Visit: [http://localhost:8089](http://localhost:8089)
