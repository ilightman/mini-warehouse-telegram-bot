import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from db_api.deta_db.services import get_box_by_id, get_content_by_id, delete_content_by_content_id, delete_box
from misc.keyboards import box_inl_kb, box_content_inl_kb, cb_kb
from misc.views import box_view, EXAMPLE_BOXES_TEXT, all_boxes_view


async def edit_cb(cb: types.CallbackQuery, callback_data: dict, state: FSMContext):
    user_id = cb.from_user.id
    box_id, action = callback_data.get('box_id'), callback_data.get('action')

    if box_id == str(user_id):
        await cb.answer(EXAMPLE_BOXES_TEXT, show_alert=True)
        return

    await cb.answer()
    if action == 'edit_contents':
        await cb.message.delete()
        msg_dict = await box_view(user_id=user_id, box_id=box_id)
        await cb.message.answer(msg_dict['text'] + "\n\nЧто добавить (через запятую)?",
                                reply_markup=msg_dict['reply_markup'])
        await state.update_data(box_id=box_id)
        await state.set_state("add_contents")
    elif action in ('edit_name', 'edit_place'):
        box = await get_box_by_id(user_id=user_id, box_id=box_id)
        await cb.message.delete()
        if 'name' in action:
            msg = f"Текущее имя: <code>{box.get('box_name')}</code>\nВведите новое"
        else:
            msg = f"Текущее место: <code>{box.get('place')}</code>\nВведите новое"
        await cb.message.answer(msg, reply_markup=box_inl_kb(box_id))
        await state.update_data(box_id=box_id)
        await state.set_state("upd_name" if 'name' in action else "upd_place")
    elif action == 'edit_items':
        contents_inl_kb = await box_content_inl_kb(box_id, 'edit_item_')
        await state.update_data(box_id=box_id)
        await cb.message.edit_reply_markup(reply_markup=contents_inl_kb)
    elif action.startswith('edit_item_'):
        content_id = action[10:]
        content = await get_content_by_id(content_id)
        await cb.message.answer(f"<code>{content.get('contents')}</code>\n"
                                f"нажми, чтобы скопировать и отправь мне исправленное")
        await state.update_data(content_id=content_id)
        await state.set_state('edit_item')


async def delete_callback_handler(cb: types.CallbackQuery, callback_data: dict):
    user_id = cb.from_user.id
    box_id, action = callback_data.get('box_id'), callback_data.get('action')

    if box_id == str(user_id):
        await cb.answer(EXAMPLE_BOXES_TEXT, show_alert=True)
        return

    await cb.answer()
    if action == 'delete_contents_by_id':
        contents_inl_kb = await box_content_inl_kb(box_id, 'delete_item_')
        await cb.message.edit_reply_markup(reply_markup=contents_inl_kb)
    elif action.startswith('delete_item_'):
        content_id = action[12:]
        await delete_content_by_content_id(content_id)
        msg_dict = await box_view(user_id=user_id, box_id=box_id, menu_only=True)
        await cb.message.edit_text(**msg_dict)
    elif action == 'delete_confirm':
        await cb.message.edit_text(f"Вы уверены что хотите \nудалить ящик № {box_id}",
                                   reply_markup=box_inl_kb(box_id, confirm_menu=True))
    logging.info(f'{cb.data}:{cb.message.from_user.id}:{cb.message.from_user.full_name}')


async def cb_query(cb: types.CallbackQuery, callback_data: dict, state: FSMContext):
    """Остальные callback"""
    user_id = cb.from_user.id
    box_id, action = callback_data.get('box_id'), callback_data.get('action')

    # await cb.answer()
    if action in ['menu', 'back']:
        await cb.message.edit_reply_markup(reply_markup=box_inl_kb(box_id, box_menu=True))
    elif action == 'confirm':

        if box_id == str(user_id):
            await cb.answer(EXAMPLE_BOXES_TEXT, show_alert=True)
            await state.finish()
            return

        await delete_box(box_id)
        await cb.message.edit_text(f"Ящик № {box_id} удален.\n\n" + await all_boxes_view(user_id=user_id))
        await state.finish()
    elif action == 'cancel':
        await cb.message.delete()
        await state.finish()
    logging.info(f'{cb.data}:{cb.message.from_user.id}:{cb.message.from_user.full_name}')


def register_callbacks(disp: Dispatcher):
    disp.register_callback_query_handler(edit_cb, cb_kb.filter(), text_contains='edit_')
    disp.register_callback_query_handler(delete_callback_handler, cb_kb.filter(), text_contains='delete_')
    disp.register_callback_query_handler(cb_query, cb_kb.filter(), state='*')
