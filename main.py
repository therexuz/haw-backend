if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.hawApp:app", host="0.0.0.0", port=8000, reload=True,log_level="debug")