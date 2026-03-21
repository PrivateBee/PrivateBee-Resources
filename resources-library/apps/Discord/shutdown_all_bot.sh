#!/bin/bash

# Project path in bp03
DIR="/volume1/discord/code"
LOG_FILE="/volume1/discord/log/output_shutdown.txt"
BOT_SCRIPT="bot_role_kick.py"
BOT_SCRIPT_GITHUB="bot_github.py"

cd "$DIR"

{
    echo "--- Session Shutdown du $(date) ---"

    # Loke for bot_role_kick's and bot_github's PID
    PID=$(ps aux | grep "$BOT_SCRIPT" | grep -v grep | awk '{print $2}')
    PID_GITHUB=$(ps aux | grep "$BOT_SCRIPT_GITHUB" | grep -v grep | awk '{print $2}')

    if [ -z "$PID" ]; then
        echo "[INFO] Le bot $BOT_SCRIPT n'est pas en cours d'ex�cution ou introuvable via ps."
    else
        echo "[ACTION] Arr�t propre du bot (PID: $PID)..."
        
        # Send SIGINT signal to bot_role_kick
        kill -2 "$PID"

        # Check if bot_role_kick is killed
        sleep 3
        if ps -p "$PID" > /dev/null; then
            echo "[WARNING] Le bot ne s'est pas arr�t�, envoi d'un signal forc�..."
            kill -9 "$PID"
        else
            echo "[SUCCESS] Le bot s'est arr�t� correctement."
        fi
    fi

    if [ -z "$PID_GITHUB" ]; then
        echo "[INFO] Le bot $BOT_SCRIPT_GITHUB n'est pas en cours d'ex�cution ou introuvable via ps."
    else
        echo "[ACTION] Arr�t propre du bot (PID: $PID_GITHUB)..."
        
        # Send SIGINT signal to bot_github
        kill -2 "$PID_GITHUB"

        # Check if bot_github is killed
        sleep 3
        if ps -p "$PID_GITHUB" > /dev/null; then
            echo "[WARNING] Le bot ne s'est pas arr�t�, envoi d'un signal forc�..."
            kill -9 "$PID_GITHUB"
        else
            echo "[SUCCESS] Le bot s'est arr�t� correctement."
        fi
    fi

} > "$LOG_FILE" 2>&1