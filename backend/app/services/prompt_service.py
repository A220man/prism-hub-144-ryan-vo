# Prompt Service
from typing import Optional
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.app.models.prompt import Prompt
from backend.app.api.schemas import PromptCreate, PromptUpdate


async def create_prompt(db: AsyncSession, prompt_in: PromptCreate) -> Prompt:
    """Create a new prompt."""
    # If this is set as default, unset other defaults for the same model
    if prompt_in.is_default:
        await unset_default_for_model(db, prompt_in.model_name)

    prompt = Prompt(
        model_name=prompt_in.model_name,
        prompt_text=prompt_in.prompt_text,
        is_default=prompt_in.is_default,
        tags=prompt_in.tags,
    )
    db.add(prompt)
    await db.flush()
    await db.refresh(prompt)
    return prompt


async def get_prompt(db: AsyncSession, prompt_id: int) -> Optional[Prompt]:
    """Get prompt by ID."""
    result = await db.execute(select(Prompt).where(Prompt.id == prompt_id))
    return result.scalar_one_or_none()


async def get_default_prompt(db: AsyncSession, model_name: str) -> Optional[Prompt]:
    """Get default prompt for a model."""
    result = await db.execute(
        select(Prompt).where(Prompt.model_name == model_name, Prompt.is_default == True)
    )
    return result.scalar_one_or_none()


async def list_prompts(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    model_name: Optional[str] = None,
    search: Optional[str] = None,
    is_default: Optional[bool] = None,
) -> tuple[list[Prompt], int]:
    """List prompts with pagination and filters."""
    query = select(Prompt)
    count_query = select(func.count(Prompt.id))

    conditions = []
    if model_name:
        conditions.append(Prompt.model_name == model_name)
    if is_default is not None:
        conditions.append(Prompt.is_default == is_default)
    if search:
        conditions.append(
            or_(
                Prompt.prompt_text.ilike(f"%{search}%"),
                Prompt.model_name.ilike(f"%{search}%"),
                Prompt.tags.ilike(f"%{search}%"),
            )
        )

    if conditions:
        query = query.where(*conditions)
        count_query = count_query.where(*conditions)

    total = (await db.execute(count_query)).scalar_one()
    query = query.order_by(Prompt.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()
    return items, total


async def update_prompt(db: AsyncSession, prompt_id: int, prompt_in: PromptUpdate) -> Optional[Prompt]:
    """Update a prompt."""
    prompt = await get_prompt(db, prompt_id)
    if not prompt:
        return None

    update_data = prompt_in.model_dump(exclude_unset=True)

    # If setting as default, unset other defaults for the same model
    if update_data.get("is_default") is True:
        model = update_data.get("model_name", prompt.model_name)
        await unset_default_for_model(db, model)

    for field, value in update_data.items():
        setattr(prompt, field, value)

    await db.flush()
    await db.refresh(prompt)
    return prompt


async def delete_prompt(db: AsyncSession, prompt_id: int) -> bool:
    """Delete a prompt."""
    prompt = await get_prompt(db, prompt_id)
    if not prompt:
        return False
    await db.delete(prompt)
    return True


async def unset_default_for_model(db: AsyncSession, model_name: str) -> None:
    """Unset default flag for all prompts of a model."""
    from sqlalchemy import update
    await db.execute(
        update(Prompt).where(Prompt.model_name == model_name, Prompt.is_default == True).values(is_default=False)
    )


async def import_prompts(db: AsyncSession, prompts_data: list[dict]) -> list[Prompt]:
    """Import multiple prompts."""
    created = []
    for data in prompts_data:
        prompt_in = PromptCreate(**data)
        prompt = await create_prompt(db, prompt_in)
        created.append(prompt)
    return created


async def export_prompts(db: AsyncSession, model_name: Optional[str] = None) -> list[Prompt]:
    """Export prompts (all or filtered by model)."""
    query = select(Prompt).order_by(Prompt.model_name, Prompt.created_at)
    if model_name:
        query = query.where(Prompt.model_name == model_name)
    result = await db.execute(query)
    return result.scalars().all()