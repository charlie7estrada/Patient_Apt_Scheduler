from fastapi import FastAPI

app = FastAPI(title="Patient Appointment Scheduler API")


@app.get("/health")
def health_check():
    return {"status": "ok"}
