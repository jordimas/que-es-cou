#claude config set trustedDirectories '["/home/jordi/sc/que-es-cou"]' --yes
python fetch.py
claude --dangerously-skip-permissions -p "Run the prompt.md task"
python render.py
