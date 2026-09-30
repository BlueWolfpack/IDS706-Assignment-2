FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MPLBACKEND=Agg

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY fxns_for_ACE.py assignment_2_ntbk.py Agrofood_co2_emission.csv ./

CMD ["python", "assignment_2_ntbk.py"]