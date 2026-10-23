# Prompts API Endpoints
from fastapi import APIRouter, Depends, HTTPException, Query, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from backend.app.core.database import get_db
from backend.app.core.security import TokenData, validate_token, require_role
from backend.app.services.prompt_service import (
    create_prompt,
    get_prompt,
    get_default_prompt,
    list_prompts,
    update_prompt,
    delete_prompt,
    import_prompts,
    export_prompts,
)
from backend.app.api.schemas import (
    PromptCreate,
    PromptUpdate,
    PromptResponse,
    PromptListResponse,
)


router = APIRouter(prefix="/api/prompts", tags=["prompts"])


async def get_current_user(authorization: str = Header(None)) -> TokenData:
    """Extract and validate token from Authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )
    token = authorization.split(" ")[1]
    return validate_token(token)

@router.post("", response_model=PromptResponse, status_code=status.HTTP_201_CREATED)
async def create_prompt_endpoint(
    prompt_in: PromptCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """Create a new prompt."""
    if not require_role(current_user, ["admin", "operator"]):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return await create_prompt(db, prompt_in)


@router.get("", response_model=PromptListResponse)
async def list_prompts_endpoint(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    model_name: Optional[str] = None,
    search: Optional[str] = None,
    is_default: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """List prompts with pagination and filters."""
    if not require_role(current_user, ["admin", "operator", "analyst"]):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    items, total = await list_prompts(db, page, page_size, model_name, search, is_default)
    total_pages = (total + page_size - 1) // page_size

    return PromptListResponse(
        items=[PromptResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/default/{model_name}", response_model=PromptResponse)
async def get_default_prompt_endpoint(
    model_name: str,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """Get default prompt for a model."""
    if not require_role(current_user, ["admin", "operator", "analyst"]):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    prompt = await get_default_prompt(db, model_name)
    if not prompt:
        raise HTTPException(status_code=404, detail=f"No default prompt found for model: {model_name}")
    return PromptResponse.model_validate(prompt)


@router.get("/{prompt_id}", response_model=PromptResponse)
async def get_prompt_endpoint(
    prompt_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """Get a prompt by ID."""
    if not require_role(current_user, ["admin", "operator", "analyst"]):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    prompt = await get_prompt(db, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return PromptResponse.model_validate(prompt)


@router.patch("/{prompt_id}", response_model=PromptResponse)
async def update_prompt_endpoint(
    prompt_id: int,
    prompt_in: PromptUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """Update a prompt."""
    if not require_role(current_user, ["admin", "operator"]):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    prompt = await update_prompt(db, prompt_id, prompt_in)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return PromptResponse.model_validate(prompt)


@router.delete("/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prompt_endpoint(
    prompt_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """Delete a prompt."""
    if not require_role(current_user, ["admin"]):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    success = await delete_prompt(db, prompt_id)
    if not success:
        raise HTTPException(status_code=404, detail="Prompt not found")


@router.post("/import", response_model=list[PromptResponse])
async def import_prompts_endpoint(
    prompts_data: list[PromptCreate],
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """Import multiple prompts."""
    if not require_role(current_user, ["admin", "operator"]):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    created = await import_prompts(db, [p.model_dump() for p in prompts_data])
    return [PromptResponse.model_validate(p) for p in created]


@router.get("/export/all", response_model=list[PromptResponse])
async def export_prompts_endpoint(
    model_name: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """Export all prompts (optionally filtered by model)."""
    if not require_role(current_user, ["admin", "operator", "analyst"]):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    prompts = await export_prompts(db, model_name)
    return [PromptResponse.model_validate(p) for p in prompts]