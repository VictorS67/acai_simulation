from app import app
from app.forms import (
    ChatForm, 
    SurveyForm,
    DiaryForm,
    PostSurveyForm
)
from app.conversation import (
    GPTConversation,
    init_reflection_bot,
)
from app.video import init_video_for_mindfulness
from app.database import (
    add_new_chat_log,
    track_link_click,
    add_new_user_to_diary_study,
    update_pre_survey,
    udpate_diary,
    update_reflect_chat,
    update_reflect,
    update_post_survey,
    get_diary_answers_from_latest_user_id
)
from flask import (
    Flask,
    request,
    session,
    jsonify,
    render_template, 
    redirect,
    url_for,
    abort
)

from datetime import datetime, timezone

# run_with_ngrok(app)

def _delete_session_variable(variable: str) -> None:
    try:
        del session[variable]
    except KeyError:
        pass

@app.route('/qualtrics', methods=['GET', 'POST'])
def start_qualtrics_conversation():
    user_id = request.remote_addr
    session["user"] = user_id
    reflection_bot = session.get("reflection_bot", None)
    if not reflection_bot:
        select_prompt = init_reflection_bot()
        reflection_bot = {
            "chat_log": select_prompt["prompt"] + select_prompt[
                "message_start"],
            "convo_start": select_prompt["message_start"],
            "bot_start": 'The following bot is designed to help you reflect on your understanding of the mindfulness video. You can start by prompting "Can you help me reflect on my understanding of mindfulness?"',
            "chatbot": select_prompt["chatbot"],
            "user": user_id,
        }
    else:
        reflection_bot["user"] = user_id

    convo = GPTConversation(
        user=reflection_bot.get("user"),
        chatbot=reflection_bot.get("chatbot"),
        chat_log=reflection_bot.get("chat_log"),
        bot_start=reflection_bot.get("bot_start"),
        convo_start=reflection_bot.get("convo_start")
    )

    start = session.get('start')
    if start is None:
        session["start"] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

    stop = session.get('stop')
    if stop is None:
        session["stop"] = 5 * 60

    now = datetime.now()
    difference = now - datetime.strptime(session.get('start'),
                                         "%m/%d/%Y, %H:%M:%S")
    difference_seconds = difference.total_seconds()

    end = session.get('end')
    if end is None or not end:
        session["end"] = (difference_seconds >= session.get('stop'))

    session["end"] = False
    form = ChatForm()
    if form.validate_on_submit() and not end:
        user_message = form.message.data
        answer = convo.ask(user_message)
        chat_log = convo.append_interaction_to_chat_log(user_message, answer)

        reflection_bot['chat_log'] = chat_log

        add_new_chat_log(reflection_bot["user"], reflection_bot["chat_log"])
        update_reflect_chat(user_id=user_id, reflect_chatlog=chat_log)

        session["reflection_bot"] = reflection_bot
        return redirect(url_for('start_qualtrics_conversation'))

    return render_template(
        '/dialogue/qualtrics_card.html',
        user=convo.get_user(),
        bot=convo.get_chatbot(),
        warning=convo.WARNING,
        end=convo.END,
        notification=convo.NOTI,
        conversation=convo.get_conversation(end=session.get('end')),
        form=form
    )


@app.route('/clear', methods=['GET'])
def clear_session():
    delete_variables = [
        'chat_log',
        'start',
        'end',
        'arm_no',
        'bot_chat_log',
        'user_chat_log',
        'mindfulness_chat_log',
        'mindfulness_dialogue_id',
        'mindfulness_dialogue_answers',
        'motivational_interview_chat_log',
        'motivational_interview_id',
        'motivational_interview_answers',
        'info_bot',
        'reflection_bot',
        'mindy',
        'reflect_diary',
        'user'
    ]
    for variable in delete_variables:
        _delete_session_variable(variable)

    return "cleared!"


# @app.route('/survey/<user_id>', methods=['GET', 'POST'])
# def survey(user_id):
#     session["user"] = user_id

#     form = SurveyForm()
#     if form.validate_on_submit():
#         presurvey_1 = form.mindful_today.data
#         presurvey_2 = form.stress.data
#         presurvey_3 = form.positive_mindset.data
#         presurvey_4 = form.decentering.data
#         print("SURVEY FORM IS SUBMITTED!!!")
#         print(f"presurvey 1: {presurvey_1}\npresurvey 2: {presurvey_2}\npresurvey 3: {presurvey_3}\npresurvey 4: {presurvey_4}")

#         update_pre_survey(
#             user_id=user_id, 
#             pre_mindful=presurvey_1, 
#             pre_stress=presurvey_2,
#             pre_aware=presurvey_3,
#             pre_perspective=presurvey_4,
#             pre_survey_click_ts=datetime.now()
#         )

#         return redirect(url_for('video_diary', user_id=user_id))
    
#     track_link_click(user_id=user_id, timestamp=datetime.now())
#     add_new_user_to_diary_study(user_id=user_id, session_start_ts=datetime.now())
    
#     delete_variables = [
#         'reflect_diary'
#     ]
#     for variable in delete_variables:
#         _delete_session_variable(variable)

#     return render_template(
#         "/pages/survey.html",
#         form=form
#     )


@app.route('/video_diary/<user_id>', methods=['GET', 'POST'])
def video_diary(user_id):
    session["user"] = user_id
    video_url = init_video_for_mindfulness()

    form = DiaryForm()
    if form.validate_on_submit():
        diary_1 = form.diary_1.data
        diary_2 = form.diary_2.data
        diary_3 = form.diary_3.data
        diary_4 = form.diary_4.data
        diary_5 = form.diary_5.data
        diary_6 = form.diary_6.data
        diary_7 = form.diary_7.data
        diary_8 = form.diary_8.data
        diary_9 = form.diary_9.data
        video_name = form.video_name.data
        print("VIDEO DIARY FORM IS SUBMITTED!!!")
        # print(f"diary 1: {diary_1}\ndiary 2: {diary_2}")
        print(f"video_name: {video_name}")

        udpate_diary(
            user_id=user_id, 
            diary_1=str(diary_1), 
            diary_2=str(diary_2), 
            diary_3=str(diary_3), 
            diary_4=str(diary_4), 
            diary_5=str(diary_5), 
            diary_6=str(diary_6), 
            diary_7=str(diary_7), 
            diary_8=str(diary_8), 
            diary_9=str(diary_9), 
            video_name=str(video_name), 
            main_interface_click_ts_1=datetime.now()
        )

        return redirect(url_for('reflect_diary', user_id=user_id))

    add_new_user_to_diary_study(user_id=user_id, session_start_ts=datetime.now())
    
    delete_variables = [
        'reflect_diary'
    ]
    for variable in delete_variables:
        _delete_session_variable(variable)

    return render_template(
        "/pages/video_diary.html", 
        video_url=video_url, 
        form=form
    )


# @app.route('/post_survey/<user_id>', methods=['GET', 'POST'])
# def post_survey(user_id):
#     session["user"] = user_id
#     form = PostSurveyForm()
#     if form.validate_on_submit():
#         stress = form.stress.data
#         statement_1 = form.statement_1.data
#         statement_2 = form.statement_2.data
#         print("POST SURVEY FORM IS SUBMITTED!!!")
#         print(f"stress: {stress}\nstatement 1: {statement_1}\nstatement 2: {statement_2}")

#         update_post_survey(
#             user_id=user_id, 
#             post_stress=stress, 
#             post_aware=statement_1, 
#             post_mindful=statement_2, 
#             post_survey_click_ts=datetime.now()
#         )

#         return redirect(url_for('end_survey', user_id=user_id))

#     return render_template(
#         "/pages/post_survey.html", 
#         form=form
#     )


@app.route('/reflect_diary/<user_id>', methods=['GET', 'POST'])
def reflect_diary(user_id):
    session["user"] = user_id
    reflect_diary = session.get("reflect_diary", None)
    start_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    if not reflect_diary:
        reflect_diary = {
            "start": start_time
        }
        session['reflect_diary'] = reflect_diary

    start = session['reflect_diary'].get('start')
    if start is None:
        session['reflect_diary']["start"] = start_time

    print(f"start time: {session['reflect_diary'].get('start')}")

    form = DiaryForm()
    if form.validate_on_submit():
        diary_1 = form.diary_1.data
        diary_2 = form.diary_2.data
        diary_3 = form.diary_3.data
        diary_4 = form.diary_4.data
        diary_5 = form.diary_5.data
        diary_6 = form.diary_6.data
        diary_7 = form.diary_7.data
        diary_8 = form.diary_8.data
        diary_9 = form.diary_9.data
        print("VIDEO DIARY FORM IS SUBMITTED!!!")
        # print(f"diary 1: {diary_1}\ndiary 2: {diary_2}")

        update_reflect(
            user_id=user_id, 
            diary_1=str(diary_1), 
            diary_2=str(diary_2), 
            diary_3=str(diary_3), 
            diary_4=str(diary_4), 
            diary_5=str(diary_5), 
            diary_6=str(diary_6), 
            diary_7=str(diary_7), 
            diary_8=str(diary_8), 
            diary_9=str(diary_9), 
            main_interface_click_ts_2=datetime.now()
        )

        return redirect(url_for('end_survey', user_id=user_id))
    
    diary_1, diary_2, diary_3, diary_4, diary_5, diary_6, diary_7, diary_8, diary_9 = get_diary_answers_from_latest_user_id(user_id)
    form.diary_1.default = diary_1 if diary_1 is not None else ''
    form.diary_2.default = diary_2 if diary_2 is not None else ''
    form.diary_3.default = diary_3 if diary_3 is not None else ''
    form.diary_4.default = diary_4 if diary_4 is not None else ''
    form.diary_5.default = diary_5 if diary_5 is not None else ''
    form.diary_6.default = diary_6 if diary_6 is not None else ''
    form.diary_7.default = diary_7 if diary_7 is not None else ''
    form.diary_8.default = diary_8 if diary_8 is not None else ''
    form.diary_9.default = diary_9 if diary_9 is not None else ''
    form.process()
    
    return render_template(
        "/pages/reflect_diary.html", 
        convo_start=session['reflect_diary'].get('start'),
        user_id=user_id,
        form=form
    )


@app.route('/reflect_bot/<user_id>/<convo_end>', defaults={'show_bot_avatar': None}, methods=['GET', 'POST'])
@app.route('/reflect_bot/<user_id>/<show_bot_avatar>/<convo_end>', methods=['GET', 'POST'])
def reflect_bot(user_id, convo_end, show_bot_avatar):
    end = bool(int(convo_end))
    session["user"] = user_id
    reflection_bot = session.get("reflection_bot", None)
    if not reflection_bot:
        select_prompt = init_reflection_bot()
        reflection_bot = {
            "chat_log": select_prompt["prompt"] + select_prompt[
                "message_start"],
            "convo_start": select_prompt["message_start"],
            "bot_start": 'The following bot is designed to help you reflect on your understanding of the mindfulness video. You can start by prompting "Can you help me reflect on my understanding of mindfulness?"',
            "chatbot": select_prompt["chatbot"],
            "user": user_id,
        }
    else:
        reflection_bot["user"] = user_id

    convo = GPTConversation(
        user=reflection_bot.get("user"),
        chatbot=reflection_bot.get("chatbot"),
        chat_log=reflection_bot.get("chat_log"),
        bot_start=reflection_bot.get("bot_start"),
        convo_start=reflection_bot.get("convo_start")
    )

    form = ChatForm()
    if form.validate_on_submit() and not end:
        user_message = form.message.data
        answer = convo.ask(user_message)
        chat_log = convo.append_interaction_to_chat_log(user_message, answer)

        reflection_bot['chat_log'] = chat_log

        add_new_chat_log(reflection_bot["user"], reflection_bot["chat_log"])
        update_reflect_chat(user_id=user_id, reflect_chatlog=chat_log)

        session["reflection_bot"] = reflection_bot
        return redirect(url_for('reflect_bot', user_id=user_id, convo_end=1 if end else 0))

    session["reflection_bot"] = reflection_bot
    return render_template(
        '/dialogue/qualtrics_card.html',
        user=convo.get_user(),
        bot=convo.get_chatbot(),
        show_bot_avatar=show_bot_avatar is not None,
        warning=convo.WARNING,
        end=convo.END,
        notification=convo.NOTI,
        conversation=convo.get_conversation(end=end),
        form=form
    )


@app.route('/end_survey/<user_id>', methods=['GET', 'POST'])
def end_survey(user_id):
    session["user"] = user_id

    delete_variables = [
        'chat_log',
        'start',
        'end',
        'arm_no',
        'bot_chat_log',
        'user_chat_log',
        'info_bot',
        'reflection_bot',
        'reflect_diary',
        'user'
    ]
    for variable in delete_variables:
        _delete_session_variable(variable)

    return render_template("/pages/end.html")
