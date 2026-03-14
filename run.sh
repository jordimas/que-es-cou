#claude config set trustedDirectories '["/home/jordi/sc/que-es-cou"]' --yes
claude --dangerously-skip-permissions -p "Run the prompt.md  task"
python render.py
