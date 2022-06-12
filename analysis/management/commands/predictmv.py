
import tushare as ts
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
import pandas as pd
import os

class Command(BaseCommand):
    help = 'Taking snapshot for investors trade account'

    def add_arguments(self, parser):
        # Named (optional) arguments
        # Named (optional) arguments
        parser.add_argument(
            '--ts_code',
            type=str,
            help='Which ts_code you want to apply the download',
        )

    def handle(self, *args, **options):
        ts_code = options['ts_code']

        fin_data = load_data('all')
        # print(fin_data.head())
        show_cor(fin_data, 'total_mv')
        

def show_cor(data, field):
    corr_matrix = data.corr()
    corr_matrix[field].sort_values(ascending=False)
    print(corr_matrix[field].sort_values(ascending=False).head(20))

def load_data(file_name):
    # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
    BASE_DIR = os.path.abspath('..')
    PROJ_ROOT = os.path.join(BASE_DIR, 'investtrack')

    FIN_DATA_PATH = os.path.join(BASE_DIR, PROJ_ROOT, 'diggings/data')

    def load_fin_data(ts_code, fin_path=FIN_DATA_PATH):
        csv = os.path.join(fin_path, 'findata_' + ts_code + '.csv')
        return pd.read_csv(csv)

    fin_data = load_fin_data(file_name)
    return fin_data
