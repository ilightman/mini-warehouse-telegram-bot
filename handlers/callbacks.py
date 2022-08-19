import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from db_api.db_services import get_box_by_id, get_content_by_id, delete_content_by_content_id, delete_box
from misc import box_from_db, inl_kb_generator, edit_contents_inl, boxes_list, cb_kb


async def edit_cb(cb: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await cb.answer()
    box_id, action = callback_data.get('box_id'), callback_data.get('action')
    if action == 'edit_contents':
        if box_id == '8uj9pqchhdfk' or box_id == 'gghua4kqgsb8':
            await cb.message.edit_text('Ящик 1 и 2 для примера, изменить их не получится - \n'
                                       'но можете создать свой /add_box')
            await cb.message.answer(await box_from_db(box_id), reply_markup=inl_kb_generator(box_id, box_menu=True))
            await state.finish()
            return
        await cb.message.delete()
        await cb.message.answer(await box_from_db(box_id) + "\n\nЧто добавить (через запятую)?",
                                reply_markup=inl_kb_generator(box_id))
        await state.update_data(box_id=box_id)
        await state.set_state("add_contents")
    elif action in ('edit_name', 'edit_place'):
        if box_id == '8uj9pqchhdfk' or box_id == 'gghua4kqgsb8':
            await cb.message.edit_text('Ящик 1 и 2 для примера, изменить их не получится - \n'
                                       'но можете создать свой /add_box')
            await cb.message.answer(await box_from_db(box_id), reply_markup=inl_kb_generator(box_id, box_menu=True))
            await state.finish()
            return
        box = await get_box_by_id(box_id)
        await cb.message.delete()
        if 'name' in action:
            msg = f"имя: <code>{box.get('box_name')}</code>"
        else:
            msg = f"место: <code>{box.get('place')}</code>"
        await cb.message.answer("Текущее " + msg + ".\nВведи новое",
                                reply_markup=inl_kb_generator(box_id))
        await state.update_data(box_id=box_id)
        await state.set_state("upd_name" if 'name' in action else "upd_place")
    elif action == 'edit_items':
        contents_inl_kb = await edit_contents_inl(box_id, 'edit_item_')
        await state.update_data(box_id='box_id')
        await cb.message.edit_reply_markup(reply_markup=contents_inl_kb)
    elif action.startswith('edit_item_'):
        if box_id == '8uj9pqchhdfk' or box_id == 'gghua4kqgsb8':
            await cb.message.edit_text('Ящик 1 и 2 для примера, изменить их не получится - \n'
                                       'но можете создать свой /add_box')
            await cb.message.answer(await box_from_db(box_id), reply_markup=inl_kb_generator(box_id, box_menu=True))
            await state.finish()
            return
        content_id = action[10:]
        content = await get_content_by_id(content_id)
        await cb.message.answer(f"<code>{content.get('contents')}</code>\n"
                                f"нажми, чтобы скопировать и отправь мне исправленное")
        await state.update_data(content_id=content_id)
        await state.set_state('edit_item')


async def delete_cb_handler(cb: types.CallbackQuery, callback_data: dict):
    await cb.answer()
    box_id, action = callback_data.get('box_id'), callback_data.get('action')
    if action == 'delete_contents_by_id':
        contents_inl_kb = await edit_contents_inl(box_id, 'delete_item_')
        await cb.message.edit_reply_markup(reply_markup=contents_inl_kb)
    elif action.startswith('delete_item_'):
        if box_id == '8uj9pqchhdfk' or box_id == 'gghua4kqgsb8':
            await cb.message.edit_text('Ящик 1 и 2 для примера, удалить содержимое, также как и ящики, не получится!\n'
                                       'Можете создать свой /add_box')
            await cb.message.answer(await box_from_db(box_id),
                                    reply_markup=inl_kb_generator(box_id, menu_only=True))
            return
        else:
            content_id = action[12:]
            await delete_content_by_content_id(content_id)
        await cb.message.edit_text(await box_from_db(box_id),
                                   reply_markup=inl_kb_generator(box_id, menu_only=True))
    elif action == 'delete_confirm':
        await cb.message.edit_text(f"Вы уверены что хотите \nудалить ящик № {box_id}",
                                   reply_markup=inl_kb_generator(box_id, confirm_menu=True))
    logging.info(f'{cb.data}:{cb.message.from_user.id}:{cb.message.from_user.full_name}')


async def cb_query(cb: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await cb.answer()
    box_id, action = callback_data.get('box_id'), callback_data.get('action')
    if action == 'menu':
        await cb.message.edit_reply_markup(reply_markup=inl_kb_generator(box_id, box_menu=True))
    elif action == 'back':
        await cb.message.edit_reply_markup(reply_markup=inl_kb_generator(box_id, box_menu=True))
    elif action == 'confirm':
        if box_id == '8uj9pqchhdfk' or box_id == 'gghua4kqgsb8':
            await cb.message.edit_text('Ящик 1 и 2 для примера, удалить содержимое, также как и ящики, не получится!\n'
                                       'Можете создать свой /add_box')
            await cb.message.answer(await box_from_db(box_id), reply_markup=inl_kb_generator(box_id, box_menu=True))
            await state.finish()
            return
        await delete_box(box_id)
        await cb.message.edit_text(f"Ящик № {box_id} удален.\n\n" + await boxes_list())
        await state.finish()
    elif action == 'cancel':
        await cb.message.delete()
        await state.finish()
    logging.info(f'{cb.data}:{cb.message.from_user.id}:{cb.message.from_user.full_name}')


def register_callbacks(disp: Dispatcher):
    disp.register_callback_query_handler(edit_cb, cb_kb.filter(), text_contains='edit_')
    disp.register_callback_query_handler(delete_cb_handler, cb_kb.filter(), text_contains='delete_')
    disp.register_callback_query_handler(cb_query, cb_kb.filter(), state='*')
