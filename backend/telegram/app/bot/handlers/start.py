from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from app.bot.keyboards.start import get_start_keyboard
from app.bot.states import AuthState
from app.utils.auth import TelegramAuthError, TelegramLoginNotFound, TelegramRegisterConflict
from app.utils.auth import telegram_auth, link_telegram
from app.config import API_BASE_URL, SECRET_TELEGRAM_AUTH_KEY

router = Router()

@router.message(F.text == "/start")
async def start_handler(message: Message, state: FSMContext):
    keyboard = get_start_keyboard()

    await message.answer(
        "👋 Привет! Выберите, что хотите сделать:",
        reply_markup=keyboard
    )

@router.callback_query(F.data == "auth_login")
async def handle_login(callback: CallbackQuery, state: FSMContext):
    try:
        data, _ = await telegram_auth(tg_id=callback.from_user.id, tg_username=callback.from_user.username, mode="login")
    except TelegramLoginNotFound:
        await callback.message.edit_text("❌ Вы не зарегистрированы. Пожалуйста, сначала пройдите регистрацию.")
        return
    except TelegramAuthError:
        await callback.message.edit_text("❌ Произошла ошибка авторизации. Обратитесь в поддержку.")
        return

    await state.set_state(AuthState.authenticated)
    await state.update_data(
        access_token=data["access_token"],
        refresh_token=data["refresh_token"],
        user_id=data["user"]["id"]
    )
    await callback.message.edit_text("👋 Добро пожаловать обратно!")


@router.callback_query(F.data == "auth_register")
async def handle_register(callback: CallbackQuery, state: FSMContext):
    try:
        data, _ = await telegram_auth(tg_id=callback.from_user.id, tg_username=callback.from_user.username, mode="register")
    except TelegramRegisterConflict:
        await callback.message.edit_text("❌ Произошла ошибка регистрации. Пользователь с вашими данными уже есть в системе.")
        return
    except TelegramAuthError:
        await callback.message.edit_text("❌ Произошла ошибка регистрации. Обратитесь в поддержку.")
        return

    await state.set_state(AuthState.authenticated)
    await state.update_data(
        access_token=data["access_token"],
        refresh_token=data["refresh_token"],
        user_id=data["user"]["id"]
    )
    await callback.message.edit_text("👋 Добро пожаловать обратно!")


@router.callback_query(F.data == "auth_link_telegram")
async def handle_link(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AuthState.waiting_for_email)
    await callback.message.edit_text("📧 Введите ваш email (example@gmail.com):")


@router.message(AuthState.waiting_for_email)
async def handle_email(message: Message, state: FSMContext):
    email = message.text.strip()
    if "@" not in email or "." not in email:
        await message.answer("⚠️ Некорректный email. Попробуйте снова:")
        return

    await state.update_data(email=email)
    await state.set_state(AuthState.waiting_for_password)
    await message.answer("🔐 Теперь введите пароль (password1!):")


@router.message(AuthState.waiting_for_password)
async def handle_password(message: Message, state: FSMContext):
    password = message.text.strip()
    data = await state.get_data()
    email = data.get("email")

    try:
        auth_data, _ = await telegram_auth(tg_id=0, tg_username='1', mode="auth_link_telegram", to_link={ "email": email, "password": password, 'remember_me': True})
    except TelegramAuthError:
        await message.answer("❌ Произошла ошибка Авторизации. Неверный логин или пароль.")
        return

    try:
        user_data, _ = await link_telegram(tg_id=message.from_user.id,
                                           tg_username = message.from_user.username or "",
                                           access_token=auth_data['access_token'])
    except TelegramAuthError:
        await message.answer("❌ Произошла ошибка связи между пользователем системы и телеграмм-аккаунтом.")
        return

    # Сохраняем токены и ID
    await state.set_state(AuthState.authenticated)
    await state.update_data(
        access_token=auth_data["access_token"],
        refresh_token=auth_data["refresh_token"],
        user_id=user_data['user']['id']
    )

    await message.answer("✅ Успешная авторизация и привязка Telegram!")
