from fastapi import APIRouter

router = APIRouter()

@router.post("/match")
async def match_resume(
):

    return {"message": "endpoint ready"}

@router.post("/extract")
async def extract_resume():
    # 
    return {"message": "endpoint ready"}