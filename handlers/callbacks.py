import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from db_api.deta_db.services import get_box, get_content_by_id, delete_content_by_content_id, delete_box
# from locales.i18n_config import i18n
from misc.keyboards import box_inl_kb, box_content_inl_kb, cb_kb
from misc.views import box_view, all_boxes_view


# _ = i18n.gettext


async def edit_cb(cb: types.CallbackQuery, callback_data: dict, state: FSMContext):
    user_id = cb.from_user.id
    box_id, action = callback_data.get('box_id'), callback_data.get('action')

    await cb.answer()
    if action == 'edit_contents':
        await cb.message.delete()
        msg_dict = await box_view(user_id=user_id, box_id=box_id)
        await cb.message.answer(msg_dict['text'] + "\n\n" + ("Что добавить (через запятую)?"),
                                reply_markup=msg_dict['reply_markup'])
        await state.update_data(box_id=box_id)
        await state.set_state("add_contents")
    elif action in ('edit_name', 'edit_place'):
        box = await get_box(user_id=user_id, box_id=box_id)
        await cb.message.delete()
        if 'name' in action:
            msg = ("Текущее имя: <code>{box_name}</code>{sn}Введите новое").format(box_name=box.name, sn='\n')
        else:
            msg = ("Текущее место: <code>{box_place}</code>{sn}Введите новое").format(box_place=box.place, sn='\n')
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
        await cb.message.answer(f"<code>{content.name}</code>\n" +
                                ("нажми, чтобы скопировать и отправь мне исправленное"))
        await state.update_data(content_id=content_id)
        await state.set_state('edit_item')


async def delete_callback_handler(cb: types.CallbackQuery, callback_data: dict):
    user_id = cb.from_user.id
    box_id, action = callback_data.get('box_id'), callback_data.get('action')
    await cb.answer()
    if action == 'delete_content':
        contents_inl_kb = await box_content_inl_kb(box_id, 'delete_item_')
        await cb.message.edit_reply_markup(reply_markup=contents_inl_kb)
    elif action.startswith('delete_item_'):
        content_id = action[12:]
        await delete_content_by_content_id(content_id)
        msg_dict = await box_view(user_id=user_id, box_id=box_id, menu_only=True)
        await cb.message.edit_text(**msg_dict)
    elif action == 'delete_confirm':
        await cb.message.edit_text(
            ("Вы уверены что хотите {sn}удалить ящик № {box_id}").format(sn='\n', box_id=box_id),
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
        await delete_box(box_id)
        await cb.message.edit_text(
            ("Ящик № {} удален.").format(box_id) + "\n\n" + await all_boxes_view(user_id=user_id))
        await state.finish()
    elif action == 'cancel':
        await cb.message.delete()
        await state.finish()
    logging.info(f'{cb.data}:{cb.message.from_user.id}:{cb.message.from_user.full_name}')


def register_callbacks(disp: Dispatcher):
    disp.register_callback_query_handler(edit_cb, cb_kb.filter(), text_contains='edit_')
    disp.register_callback_query_handler(delete_callback_handler, cb_kb.filter(), text_contains='delete_')
    disp.register_callback_query_handler(cb_query, cb_kb.filter(), state='*')
