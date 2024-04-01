if [[ "$VIRTUAL_ENV" == "" ]]
then
  python3 -m pip install --upgrade pip
  python3 -m venv .venv

  python3 -m pip install -r requirements.txt
fi

source .venv/bin/activate


