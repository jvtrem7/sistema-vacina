git clone https://github.com/jvtrem7/sistema-vacina
cd sistema_vacina


abre o terminal

python -m venv venv
.\venv\Scripts\activate

pip install django

python manage.py makemigrations
python manage.py migrate

python manage.py runserver
