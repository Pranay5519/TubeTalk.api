from fastapi import Header, HTTPException, Depends

# Dependency to extract Gemini API key from header
def get_gemini_api_key(gemini_api_key: str = Header(...)):
    if not gemini_api_key:
        raise HTTPException(status_code=401, detail="Gemini API key is required")
    return gemini_api_key

