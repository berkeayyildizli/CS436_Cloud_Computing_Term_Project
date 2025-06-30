from locust import HttpUser, task, between
import random

class UrlShortenerUser(HttpUser):
    wait_time = between(1, 3)
    host = "https://<your-cloud-run-url>"  # 👈 Add your Cloud Run endpoint here

    @task(2)
    def shorten_url(self):
        sample_url = f"https://example.com/page{random.randint(1,10000)}"
        self.client.post("/", json={"url": sample_url})

    @task(1)
    def redirect(self):
        # You can skip or mock this call if `test123` doesn't exist
        self.client.get("http://34.16.62.249/redirect?code=test123", name="/redirect")
