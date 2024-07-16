
import os
from flask import Flask, request, send_from_directory
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, LocationMessage, TextSendMessage
import dotenv
import geo_utils
dotenv.load_dotenv()
app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

@app.route('/callback', methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    handler.handle(body, signature)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextMessage(text=event.message.text)
    )

@handler.add(MessageEvent, message=LocationMessage)
def handle_location(event):
    user_lat = event.message.latitude
    user_lon = event.message.longitude
    user_id = event.source.user_id

    top_five_stations = geo_utils.get_nearby_stations(user_lat, user_lon, max_distance=1000)
    map_file = geo_utils.generate_map(user_lat, user_lon, top_five_stations, user_id)

    # 构建地图文件的URL
    map_url = f"https://3860-203-72-100-252.ngrok-free.app/static/{map_file}"

    # 發送結果
    messages = [
        TextSendMessage(text=f"找到離你最近的 5 個單車站點：\n" + "\n".join(
            [f"{row['sna']} - {row['distance']:.2f}m\nGoogle Maps:\
                {row['google_maps_link']}" for _, row in top_five_stations.iterrows()]
        )),
        TextSendMessage(text=f"完整地圖：\n{map_url}")
    ]

    line_bot_api.reply_message(event.reply_token, messages)

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(port=5050)