#!/bin/bash

# Project path in bp03
DIR="/volume1/discord/code"
LOG_FILE="/volume1/discord/log/output_discord.txt"
cd "$DIR"

{
    echo "--- Session du $(date) ---"

    # Make a venv if necessary 
    if [ ! -d "venv" ]; then
        echo "--- Création de l'environnement virtuel ---"
        python3 -m venv venv
    fi

    # Activate the venv
    source venv/bin/activate

    # Update dependancies 
    echo "--- Vérification des dépendances ---"
    pip install -r requirements.txt

    # Run bot
    echo "--- Lancement du Bot git ---"
    python3 -u bot_github.py 
    
    wait

} > "$LOG_FILE" 2>>&1