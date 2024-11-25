import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from django.conf import settings
from django.shortcuts import get_object_or_404
import threading
from django.db.utils import IntegrityError

# Bot settings
bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN)

# User states
USER_STATE = {}

# Buttons
def main_menu_buttons():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("/register"))
    markup.add(KeyboardButton("/login"))
    return markup

def attendance_buttons():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("/omadam"), KeyboardButton("/raftam"))
    markup.add(KeyboardButton("/der_mekunam"), KeyboardButton("/nameoyam"))
    markup.add(KeyboardButton("/logout"))
    return markup

def group_buttons():
    from .models import Group
    groups = Group.objects.all()
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for group in groups:
        markup.add(KeyboardButton(group.name))
    return markup

# Command: /start
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    bot.send_message(
        user_id,
        "Хуш омадед ба системаи ҳозирии донишҷӯён!\nИнтихоб кунед:",
        reply_markup=main_menu_buttons()
    )
    USER_STATE[user_id] = {'state': 'start'}

@bot.message_handler(commands=['register'])
def register(message):
    user_id = message.chat.id
    bot.send_message(user_id, "Лутфан номи пурраи худро ворид кунед (Номи аввал ва насаб):")
    USER_STATE[user_id] = {'state': 'waiting_for_name'}

@bot.message_handler(func=lambda message: USER_STATE.get(message.chat.id, {}).get('state') == 'waiting_for_name')
def handle_name(message):
    user_id = message.chat.id
    full_name = message.text.split()
    if len(full_name) == 2:
        USER_STATE[user_id] = {
            'state': 'waiting_for_phone',
            'f_name': full_name[0],
            'l_name': full_name[1]
        }
        bot.send_message(user_id, "Лутфан рақами телефони худро ворид кунед:")
    else:
        bot.send_message(user_id, "Илтимос, номи худро дар шакли дуруст (Ном Насаб) ворид кунед.")

@bot.message_handler(func=lambda message: USER_STATE.get(message.chat.id, {}).get('state') == 'waiting_for_phone')
def handle_phone(message):
    user_id = message.chat.id
    phone = message.text
    if phone.isdigit() and len(phone) >= 7:  # Simple phone validation
        USER_STATE[user_id]['phone'] = phone
        bot.send_message(user_id, "Лутфан почтаи электронии худро ворид кунед:")
        USER_STATE[user_id]['state'] = 'waiting_for_email'
    else:
        bot.send_message(user_id, "Рақами телефон нодуруст аст. Лутфан дубора кӯшиш кунед:")

@bot.message_handler(func=lambda message: USER_STATE.get(message.chat.id, {}).get('state') == 'waiting_for_email')
def handle_email(message):
    user_id = message.chat.id
    email = message.text
    if "@" in email and "." in email:  # Simple email validation
        USER_STATE[user_id]['email'] = email
        bot.send_message(user_id, "Лутфан номи корбарии худро (username) ворид кунед:")
        USER_STATE[user_id]['state'] = 'waiting_for_username'
    else:
        bot.send_message(user_id, "Почтаи электронӣ нодуруст аст. Лутфан дубора кӯшиш кунед:")

@bot.message_handler(func=lambda message: USER_STATE.get(message.chat.id, {}).get('state') == 'waiting_for_username')
def handle_username(message):
    user_id = message.chat.id
    username = message.text

    from .models import Students
    try:
        student = Students.objects.create(
            f_name=USER_STATE[user_id]['f_name'],
            l_name=USER_STATE[user_id]['l_name'],
            phone=USER_STATE[user_id]['phone'],
            email=USER_STATE[user_id]['email'],
            username=username,
            is_active=True
        )
        bot.send_message(user_id, f"Сабти ном муваффақ шуд! Хуш омадед, {student.f_name} {student.l_name}!\nҲоло гурӯҳро интихоб кунед:", 
                         reply_markup=group_buttons())
        USER_STATE[user_id] = {'state': 'waiting_for_group', 'student_id': student.id}
    except IntegrityError:
        bot.send_message(user_id, "Ин номи корбарӣ аллакай мавҷуд аст. Лутфан номи дигарро интихоб кунед.")
        USER_STATE[user_id]['state'] = 'waiting_for_username'


@bot.message_handler(func=lambda message: USER_STATE.get(message.chat.id, {}).get('state') == 'waiting_for_group')
def handle_group(message):
    user_id = message.chat.id
    group_name = message.text
    from .models import Group, Students

    try:
        group = Group.objects.get(name=group_name)
        student = Students.objects.get(id=USER_STATE[user_id]['student_id'])
        student.group.add(group)
        student.save()
        bot.send_message(user_id, "Гурӯҳ муваффақона интихоб шуд! Сабти ҳозирӣ оғоз мешавад.", reply_markup=main_menu_buttons())
        USER_STATE.pop(user_id)
    except Group.DoesNotExist:
        bot.send_message(user_id, "Гурӯҳ ёфт нашуд. Лутфан гурӯҳи дурустро интихоб кунед.")


@bot.message_handler(commands=['login'])
def login(message):
    user_id = message.chat.id
    bot.send_message(user_id, "Лутфан номи пурраи худро ва номи корбариро ворид кунед (Ном Насаб username):")
    USER_STATE[user_id] = {'state': 'waiting_for_login'}

@bot.message_handler(func=lambda message: USER_STATE.get(message.chat.id, {}).get('state') == 'waiting_for_login')
def handle_login(message):
    user_id = message.chat.id
    user_input = message.text.split()
    if len(user_input) == 3:
        f_name, l_name, username = user_input
        from .models import Students
        try:
            student = Students.objects.get(f_name=f_name, l_name=l_name, username=username)
            bot.send_message(
                user_id,
                f"Шумо бомуваффақият ворид шудед! Хуш омадед, {student.f_name}!",
                reply_markup=attendance_buttons()
            )
            USER_STATE[user_id] = {'state': 'attendance', 'student_id': student.id}
        except Students.DoesNotExist:
            bot.send_message(user_id, "Донишҷӯ ёфт нашуд. Лутфан маълумоти дурустро ворид кунед.")
    else:
        bot.send_message(user_id, "Маълумоти худро дар шакли дуруст (Ном Насаб username) ворид кунед.")
        


@bot.message_handler(commands=['logout'])
def logout(message):
    user_id = message.chat.id
    if user_id in USER_STATE:
        USER_STATE.pop(user_id)
    bot.send_message(
        user_id,
        "Шумо бомуваффақият аз система хориҷ шудед!",
        reply_markup=main_menu_buttons()
    )
@bot.message_handler(commands=['omadam'])
def omadam(message):
    user_id = message.chat.id
    from .models import Attendance, Students
    student_id = USER_STATE[user_id]['student_id']
    student = get_object_or_404(Students, id=student_id)
    Attendance.objects.create(student=student, omadan=True)
    
    # Remove "Der Mekunam" and "Nameoyam" buttons when "Omadam" is selected
    bot.send_message(
        user_id,
        "Шумо ҳозир шудед. Сабт шуд!",
        reply_markup=attendance_buttons(der_mekunam_selected=True,nameoyam_selected=True)
    )


@bot.message_handler(commands=['raftam'])
def raftam(message):
    user_id = message.chat.id
    from .models import Attendance, Students
    student_id = USER_STATE[user_id]['student_id']
    student = get_object_or_404(Students, id=student_id)
    Attendance.objects.create(student=student, raftan=True)
    
    # Remove "Omadam", "Der Mekunam", and "Nameoyam" buttons when "Raftam" is selected
    bot.send_message(
        user_id,
        "Рафтан сабт шуд!",
        reply_markup=attendance_buttons(der_mekunam_selected=True,nameoyam_selected=True,omadam_selected=True)
    )


@bot.message_handler(commands=['der_mekunam'])
def der_mekunam(message):
    user_id = message.chat.id
    bot.send_message(user_id, "Лутфан сабаби дер омаданро ворид кунед:")
    USER_STATE[user_id]['state'] = 'waiting_for_late_reason'


@bot.message_handler(func=lambda message: USER_STATE.get(message.chat.id, {}).get('state') == 'waiting_for_late_reason')
def save_late_reason(message):
    user_id = message.chat.id
    reason = message.text
    from .models import Attendance, Students
    student_id = USER_STATE[user_id]['student_id']
    student = get_object_or_404(Students, id=student_id)
    Attendance.objects.create(student=student, der_mekunam=reason)
    
    # Remove "Omadam" and "Raftam" buttons when "Der Mekunam" is selected
    bot.send_message(user_id,"Сабаби дер омадан сабт шуд!")


@bot.message_handler(commands=['nameoyam'])
def nameoyam(message):
    user_id = message.chat.id
    bot.send_message(user_id, "Лутфан сабаби наомаданро ворид кунед:")
    USER_STATE[user_id]['state'] = 'waiting_for_not_coming_reason'


@bot.message_handler(func=lambda message: USER_STATE.get(message.chat.id, {}).get('state') == 'waiting_for_not_coming_reason')
def save_not_coming_reason(message):
    user_id = message.chat.id
    reason = message.text
    from .models import Attendance, Students
    student_id = USER_STATE[user_id]['student_id']
    student = get_object_or_404(Students, id=student_id)
    Attendance.objects.create(student=student, nameoyam=reason)
    
    # Remove "Omadam" and "Raftam" buttons when "Nameoyam" is selected
    bot.send_message(
        user_id,
        "Сабаби наомадан сабт шуд!",
        reply_markup=attendance_buttons(der_mekunam_selected=True,raftam_selected=True,omadam_selected=True,nameoyam_selected=True)
    )


# Update attendance buttons function to hide certain buttons based on state
def attendance_buttons(omadam_selected=False, raftam_selected=False, der_mekunam_selected=False, nameoyam_selected=False):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    
    # Only show "Omadam" if it's not selected already
    if not omadam_selected:
        markup.add(KeyboardButton("/omadam"))
    
    # Only show "Raftam" if it's not selected already
    if not raftam_selected:
        markup.add(KeyboardButton("/raftam"))
    
    # Only show "Der Mekunam" if it's not selected already
    if not der_mekunam_selected:
        markup.add(KeyboardButton("/der_mekunam"))
    
    # Only show "Nameoyam" if it's not selected already
    if not nameoyam_selected:
        markup.add(KeyboardButton("/nameoyam"))
    
    markup.add(KeyboardButton("/logout"))
    return markup

def run_django():
    from django.core.management import execute_from_command_line
    execute_from_command_line(["manage.py", "runserver"])

def run_bot():
    bot.polling(none_stop=True)

def start_server():
    threading.Thread(target=run_bot).start()
    run_django()

if __name__ == "__main__":
    start_server()