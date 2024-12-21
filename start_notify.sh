SCRIPT_DIR=$(dirname "$(readlink -f "$0")")

# 定義 tmux 會話名稱
SESSION_NAME_TRADE="coin_notify"

tmux new-session -d -s $SESSION_NAME_TRADE

tmux send-keys -t $SESSION_NAME_TRADE "cd $SCRIPT_DIR && python3 ./main.py" C-m