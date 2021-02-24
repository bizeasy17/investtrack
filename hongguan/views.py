import pandas as pd
import numpy as np
import tushare as ts
import logging
import pytz
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render, reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
from users.models import UserActionTrace, UserQueryTrace
from analysis.utils import get_ip
# Create your views here.

logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    # template_name属性用于指定使用哪个模板进行渲染
    template_name = 'hongguan/home.html'

    # context_object_name属性用于给上下文变量取名（在模板中使用该名字）
    context_object_name = 'hongguan'

    def get(self, request, *args, **kwargs):
        try:
            return render(request, self.template_name)
        except Exception as err:
            logger.error(err)


def get_money_supply(request, start_m, end_m):
    if request.method == 'GET':
        pro = ts.pro_api()

        m0_list = []
        m0_yoy_list = []
        m0_mom_list = []
        m0_qt50_list = []
        m0_yoy_qt50_list = []
        m0_mom_qt50_list = []
        m1_list = []
        m1_yoy_list = []
        m1_mom_list = []
        m1_qt50_list = []
        m1_yoy_qt50_list = []
        m1_mom_qt50_list = []
        m2_list = []
        m2_yoy_list = []
        m2_mom_list = []
        m2_qt50_list = []
        m2_yoy_qt50_list = []
        m2_mom_qt50_list = []
        m_range = []
        date_label = []

        try:
            df = pro.cn_m(start_m=start_m, end_m=end_m)
            m0_50qt = df['m0'].quantile() if df['m0'].quantile(
            ) is not None and not np.isnan(df['m0'].quantile()) else 0
            m0_yoy_50qt = df['m0_yoy'].quantile() if df['m0_yoy'].quantile(
            ) is not None and not np.isnan(df['m0_yoy'].quantile()) else 0
            m0_mom_50qt = df['m0_mom'].quantile() if df['m0_mom'].quantile(
            ) is not None and not np.isnan(df['m0_mom'].quantile()) else 0
            m1_50qt = df['m1'].quantile() if df['m1'].quantile(
            ) is not None and not np.isnan(df['m1'].quantile()) else 0
            m1_yoy_50qt = df['m1_yoy'].quantile() if df['m1_yoy'].quantile(
            ) is not None and not np.isnan(df['m1_yoy'].quantile()) else 0
            m1_mom_50qt = df['m1_mom'].quantile() if df['m1_mom'].quantile(
            ) is not None and not np.isnan(df['m1_mom'].quantile()) else 0
            m2_50qt = df['m2'].quantile() if df['m2'].quantile(
            ) is not None and not np.isnan(df['m2'].quantile()) else 0
            m2_yoy_50qt = df['m2_yoy'].quantile() if df['m2_yoy'].quantile(
            ) is not None and not np.isnan(df['m2_yoy'].quantile()) else 0
            m2_mom_50qt = df['m2_mom'].quantile() if df['m2_mom'].quantile(
            ) is not None and not np.isnan(df['m2_mom'].quantile()) else 0

            m_range.append(75)
            m_range.append(100)

            if df is not None and len(df) > 0:
                for index, row in df.iterrows():
                    date_label.append(row['month'])
                    m0_list.append(row['m0']
                                   if row['m0'] is not None and not np.isnan(row['m0']) else 0)
                    m0_yoy_list.append(row['m0_yoy'] if row['m0_yoy'] is not None and not np.isnan(
                        row['m0_yoy']) else 0)
                    m0_mom_list.append(
                        row['m0_mom'] if row['m0_mom'] is not None and not np.isnan(row['m0_mom']) else 0)
                    m0_qt50_list.append(m0_50qt)
                    m0_yoy_qt50_list.append(m0_yoy_50qt)
                    m0_mom_qt50_list.append(m0_mom_50qt)

                    m1_list.append(row['m1']
                                   if row['m1'] is not None and not np.isnan(row['m1']) else 0)
                    m1_yoy_list.append(row['m1_yoy'] if row['m1_yoy'] is not None and not np.isnan(
                        row['m1_yoy']) else 0)
                    m1_mom_list.append(
                        row['m1_mom'] if row['m1_mom'] is not None and not np.isnan(row['m1_mom']) else 0)
                    m1_qt50_list.append(m1_50qt)
                    m1_yoy_qt50_list.append(m1_yoy_50qt)
                    m1_mom_qt50_list.append(m1_mom_50qt)

                    m2_list.append(row['m2']
                                   if row['m2'] is not None and not np.isnan(row['m0']) else 0)
                    m2_yoy_list.append(row['m2_yoy'] if row['m2_yoy'] is not None and not np.isnan(
                        row['m2_yoy']) else 0)
                    m2_mom_list.append(
                        row['m2_mom'] if row['m2_mom'] is not None and not np.isnan(row['m2_mom']) else 0)
                    m2_qt50_list.append(m2_50qt)
                    m2_yoy_qt50_list.append(m2_yoy_50qt)
                    m2_mom_qt50_list.append(m2_mom_50qt)

                return JsonResponse({'date_label': date_label[::-1],
                                     'm0': m0_list[::-1],
                                     'm0_yoy': m0_yoy_list[::-1], 'm0_mom': m0_mom_list[::-1],
                                     'm0_qt50': m0_qt50_list[::-1], 'm0_yoy_qt50': m0_yoy_qt50_list[::-1],
                                     'm0_mom_qt50': m0_mom_qt50_list[::-1],
                                     'm1': m1_list[::-1],
                                     'm1_yoy': m1_yoy_list[::-1], 'm0_mom': m1_mom_list[::-1],
                                     'm1_qt50': m1_qt50_list[::-1], 'm0_yoy_qt50': m1_yoy_qt50_list[::-1],
                                     'm1_mom_qt50': m1_mom_qt50_list[::-1],
                                     'm2': m2_list[::-1],
                                     'm2_yoy': m2_yoy_list[::-1], 'm2_mom': m2_mom_list[::-1],
                                     'm2_qt50': m2_qt50_list[::-1], 'm2_yoy_qt50': m2_yoy_qt50_list[::-1],
                                     'm2_mom_qt50': m2_mom_qt50_list[::-1],
                                     'm_range': m_range}, safe=False)
            else:
                return HttpResponse(status=404)
        except Exception as err:
            logger.error(err)
            return HttpResponse(status=500)


def get_cpi(request, start_m, end_m):
    if request.method == 'GET':
        pro = ts.pro_api()

        nt_list = []
        nt_yoy_list = []
        nt_mom_list = []
        nt_accu_list = []
        nt_qt50_list = []
        nt_yoy_qt50_list = []
        nt_mom_qt50_list = []
        nt_accu_qt50_list = []
        town_list = []
        town_yoy_list = []
        town_mom_list = []
        town_accu_list = []
        town_qt50_list = []
        town_yoy_qt50_list = []
        town_mom_qt50_list = []
        town_accu_qt50_list = []
        cnt_list = []
        cnt_yoy_list = []
        cnt_mom_list = []
        cnt_accu_list = []
        cnt_qt50_list = []
        cnt_yoy_qt50_list = []
        cnt_mom_qt50_list = []
        cnt_accu_qt50_list = []
        m_range = []
        date_label = []

        try:
            df = pro.cn_cpi(start_m=start_m, end_m=end_m)
            nt_qt50 = df['nt_val'].quantile() if df['nt_val'].quantile(
            ) is not None and not np.isnan(df['nt_val'].quantile()) else 0
            nt_yoy_50qt = df['nt_yoy'].quantile() if df['nt_yoy'].quantile(
            ) is not None and not np.isnan(df['nt_yoy'].quantile()) else 0
            nt_mom_50qt = df['nt_mom'].quantile() if df['nt_mom'].quantile(
            ) is not None and not np.isnan(df['nt_mom'].quantile()) else 0
            nt_accu_50qt = df['nt_accu'].quantile() if df['nt_accu'].quantile(
            ) is not None and not np.isnan(df['nt_accu'].quantile()) else 0

            town_qt50 = df['town_val'].quantile() if df['town_val'].quantile(
            ) is not None and not np.isnan(df['town_val'].quantile()) else 0
            town_yoy_50qt = df['town_yoy'].quantile() if df['town_yoy'].quantile(
            ) is not None and not np.isnan(df['town_yoy'].quantile()) else 0
            town_mom_50qt = df['town_mom'].quantile() if df['town_mom'].quantile(
            ) is not None and not np.isnan(df['town_mom'].quantile()) else 0
            town_accu_50qt = df['town_accu'].quantile() if df['town_accu'].quantile(
            ) is not None and not np.isnan(df['town_accu'].quantile()) else 0

            cnt_qt50 = df['cnt_val'].quantile() if df['cnt_val'].quantile(
            ) is not None and not np.isnan(df['cnt_val'].quantile()) else 0
            cnt_yoy_50qt = df['cnt_yoy'].quantile() if df['cnt_yoy'].quantile(
            ) is not None and not np.isnan(df['cnt_yoy'].quantile()) else 0
            cnt_mom_50qt = df['cnt_mom'].quantile() if df['cnt_mom'].quantile(
            ) is not None and not np.isnan(df['cnt_mom'].quantile()) else 0
            cnt_accu_50qt = df['cnt_accu'].quantile() if df['cnt_accu'].quantile(
            ) is not None and not np.isnan(df['cnt_accu'].quantile()) else 0

            m_range.append(75)
            m_range.append(100)

            if df is not None and len(df) > 0:
                for index, row in df.iterrows():
                    date_label.append(row['month'])
                    nt_list.append(row['nt_val']
                                   if row['nt_val'] is not None and not np.isnan(row['nt_val']) else 0)
                    nt_yoy_list.append(row['nt_yoy'] if row['nt_yoy'] is not None and not np.isnan(
                        row['nt_yoy']) else 0)
                    nt_mom_list.append(
                        row['nt_mom'] if row['nt_mom'] is not None and not np.isnan(row['nt_mom']) else 0)
                    nt_accu_list.append(
                        row['nt_accu'] if row['nt_accu'] is not None and not np.isnan(row['nt_accu']) else 0)
                    nt_qt50_list.append(nt_qt50)
                    nt_yoy_qt50_list.append(nt_yoy_50qt)
                    nt_mom_qt50_list.append(nt_mom_50qt)
                    nt_mom_qt50_list.append(nt_accu_50qt)

                    town_list.append(row['town_val']
                                     if row['town_val'] is not None and not np.isnan(row['town_val']) else 0)
                    town_yoy_list.append(row['town_yoy'] if row['town_yoy'] is not None and not np.isnan(
                        row['town_yoy']) else 0)
                    town_mom_list.append(
                        row['town_mom'] if row['town_mom'] is not None and not np.isnan(row['town_mom']) else 0)
                    town_accu_list.append(
                        row['town_accu'] if row['town_accu'] is not None and not np.isnan(row['town_accu']) else 0)
                    town_qt50_list.append(town_qt50)
                    town_yoy_qt50_list.append(town_yoy_50qt)
                    town_mom_qt50_list.append(town_mom_50qt)
                    town_mom_qt50_list.append(town_accu_50qt)

                    cnt_list.append(row['cnt_val']
                                    if row['cnt_val'] is not None and not np.isnan(row['cnt_val']) else 0)
                    cnt_yoy_list.append(row['cnt_yoy'] if row['cnt_yoy'] is not None and not np.isnan(
                        row['cnt_yoy']) else 0)
                    cnt_mom_list.append(
                        row['cnt_mom'] if row['cnt_mom'] is not None and not np.isnan(row['cnt_mom']) else 0)
                    cnt_accu_list.append(
                        row['cnt_accu'] if row['cnt_accu'] is not None and not np.isnan(row['cnt_accu']) else 0)
                    cnt_qt50_list.append(cnt_qt50)
                    cnt_yoy_qt50_list.append(cnt_yoy_50qt)
                    cnt_mom_qt50_list.append(cnt_mom_50qt)
                    cnt_mom_qt50_list.append(cnt_accu_50qt)

                return JsonResponse({'date_label': date_label[::-1],
                                     'nt': nt_list[::-1],
                                     'nt_yoy': nt_yoy_list[::-1], 'nt_mom': nt_mom_list[::-1],
                                     'nt_qt50': nt_qt50_list[::-1], 'nt_yoy_qt50': nt_yoy_qt50_list[::-1],
                                     'nt_mom_qt50': nt_mom_qt50_list[::-1], 'nt_accu_qt50': nt_accu_qt50_list[::-1],
                                     'town': town_list[::-1],
                                     'town_yoy': town_yoy_list[::-1], 'town_mom': town_mom_list[::-1],
                                     'town_qt50': town_qt50_list[::-1], 'town_yoy_qt50': town_yoy_qt50_list[::-1],
                                     'town_mom_qt50': town_mom_qt50_list[::-1], 'town_accu_qt50': town_accu_qt50_list[::-1],
                                     'cnt': cnt_list[::-1],
                                     'cnt_yoy': cnt_yoy_list[::-1], 'cnt_mom': cnt_mom_list[::-1],
                                     'cnt_qt50': cnt_qt50_list[::-1], 'cnt_yoy_qt50': cnt_yoy_qt50_list[::-1],
                                     'cnt_mom_qt50': cnt_mom_qt50_list[::-1], 'cnt_accu_qt50': cnt_accu_qt50_list[::-1],
                                     'm_range': m_range}, safe=False)
            else:
                return HttpResponse(status=404)
        except Exception as err:
            logger.error(err)
            return HttpResponse(status=500)


def get_ppi(request, start_m, end_m):
    if request.method == 'GET':
        pro = ts.pro_api()

        ppi_yoy_list = []
        ppi_mp_yoy_list = []
        ppi_mp_qm_yoy_list = []
        ppi_mp_rm_yoy_list = []
        ppi_mp_p_yoy_list = []
        ppi_mp_cg_yoy_list = []
        ppi_mp_cg_f_yoy_list = []
        ppi_mp_cg_c_yoy_list = []
        ppi_mp_cg_adu_yoy_list = []
        ppi_mp_cg_dcg_yoy_list = []
        ppi_yoy_qt50_list = []

        ppi_mom_list = []
        ppi_mp_mom_list = []
        ppi_mp_qm_mom_list = []
        ppi_mp_rm_mom_list = []
        ppi_mp_p_mom_list = []
        ppi_mp_cg_mom_list = []
        ppi_mp_cg_f_mom_list = []
        ppi_mp_cg_c_mom_list = []
        ppi_mp_cg_adu_mom_list = []
        ppi_mp_cg_dcg_mom_list = []
        ppi_mom_qt50_list = []

        ppi_accu_list = []
        ppi_mp_accu_list = []
        ppi_mp_qm_accu_list = []
        ppi_mp_rm_accu_list = []
        ppi_mp_p_accu_list = []
        ppi_mp_cg_accu_list = []
        ppi_mp_cg_f_accu_list = []
        ppi_mp_cg_c_accu_list = []
        ppi_mp_cg_adu_accu_list = []
        ppi_mp_cg_dcg_accu_list = []
        ppi_accu_qt50_list = []

        m_range = []
        date_label = []

        try:
            df = pro.cn_ppi(start_m=start_m, end_m=end_m)
            ppi_yoy_50qt = df['ppi_yoy'].quantile() if df['ppi_yoy'].quantile(
            ) is not None and not np.isnan(df['ppi_yoy'].quantile()) else 0
            ppi_mom_50qt = df['ppi_mom'].quantile() if df['ppi_mom'].quantile(
            ) is not None and not np.isnan(df['ppi_mom'].quantile()) else 0
            ppi_accu_50qt = df['ppi_accu'].quantile() if df['ppi_accu'].quantile(
            ) is not None and not np.isnan(df['ppi_accu'].quantile()) else 0

            m_range.append(75)
            m_range.append(100)

            if df is not None and len(df) > 0:
                for index, row in df.iterrows():
                    date_label.append(row['month'])
                    ppi_yoy_list.append(row['ppi_yoy']
                                        if row['ppi_yoy'] is not None and not np.isnan(row['ppi_yoy']) else 0)
                    ppi_mp_yoy_list.append(row['ppi_mp_yoy'] if row['ppi_mp_yoy'] is not None and not np.isnan(
                        row['ppi_mp_yoy']) else 0)
                    ppi_mp_qm_yoy_list.append(row['ppi_mp_qm_yoy'] if row['ppi_mp_qm_yoy'] is not None and not np.isnan(
                        row['ppi_mp_qm_yoy']) else 0)
                    ppi_mp_rm_yoy_list.append(
                        row['ppi_mp_rm_yoy'] if row['ppi_mp_rm_yoy'] is not None and not np.isnan(row['ppi_mp_rm_yoy']) else 0)
                    ppi_mp_p_yoy_list.append(
                        row['ppi_mp_p_yoy'] if row['ppi_mp_p_yoy'] is not None and not np.isnan(row['ppi_mp_p_yoy']) else 0)
                    ppi_yoy_qt50_list.append(ppi_yoy_50qt)

                    ppi_mom_list.append(row['ppi_mom']
                                        if row['ppi_mom'] is not None and not np.isnan(row['ppi_mom']) else 0)
                    ppi_mp_mom_list.append(row['ppi_mp_mom'] if row['ppi_mp_mom'] is not None and not np.isnan(
                        row['ppi_mp_mom']) else 0)
                    ppi_mp_qm_mom_list.append(row['ppi_mp_qm_mom'] if row['ppi_mp_qm_mom'] is not None and not np.isnan(
                        row['ppi_mp_qm_mom']) else 0)
                    ppi_mp_rm_mom_list.append(
                        row['ppi_mp_rm_mom'] if row['ppi_mp_rm_mom'] is not None and not np.isnan(row['ppi_mp_rm_mom']) else 0)
                    ppi_mp_p_mom_list.append(
                        row['ppi_mp_p_mom'] if row['ppi_mp_p_mom'] is not None and not np.isnan(row['ppi_mp_p_mom']) else 0)
                    ppi_mom_qt50_list.append(ppi_mom_50qt)

                    ppi_accu_list.append(row['ppi_accu']
                                         if row['ppi_accu'] is not None and not np.isnan(row['ppi_accu']) else 0)
                    ppi_mp_accu_list.append(row['ppi_mp_accu'] if row['ppi_mp_accu'] is not None and not np.isnan(
                        row['ppi_mp_accu']) else 0)
                    ppi_mp_qm_accu_list.append(row['ppi_mp_qm_accu'] if row['ppi_mp_qm_accu'] is not None and not np.isnan(
                        row['ppi_mp_qm_accu']) else 0)
                    ppi_mp_rm_accu_list.append(
                        row['ppi_mp_rm_accu'] if row['ppi_mp_rm_accu'] is not None and not np.isnan(row['ppi_mp_rm_accu']) else 0)
                    ppi_mp_p_accu_list.append(
                        row['ppi_mp_p_accu'] if row['ppi_mp_p_accu'] is not None and not np.isnan(row['ppi_mp_p_accu']) else 0)
                    ppi_accu_qt50_list.append(ppi_accu_50qt)

                return JsonResponse({'date_label': date_label[::-1],
                                     'ppi_yoy': ppi_yoy_list[::-1],
                                     'ppi_mp_yoy': ppi_mp_yoy_list[::-1], 'ppi_mp_qm_yoy': ppi_mp_qm_yoy_list[::-1],
                                     'ppi_mp_rm_yoy': ppi_mp_rm_yoy_list[::-1], 'ppi_mp_p_yoy': ppi_mp_p_yoy_list[::-1],
                                     'ppi_yoy_qt50': ppi_yoy_qt50_list,

                                     'ppi_mom': ppi_mom_list[::-1],
                                     'ppi_mp_mom': ppi_mp_mom_list[::-1], 'ppi_mp_qm_yoy': ppi_mp_qm_mom_list[::-1],
                                     'ppi_mp_rm_mom': ppi_mp_rm_mom_list[::-1], 'ppi_mp_p_yoy': ppi_mp_p_mom_list[::-1],
                                     'ppi_mom_qt50': ppi_mom_qt50_list,

                                     'ppi_accu': ppi_accu_list[::-1],
                                     'ppi_mp_accu': ppi_mp_accu_list[::-1], 'ppi_mp_qm_accu': ppi_mp_qm_accu_list[::-1],
                                     'ppi_mp_rm_accu': ppi_mp_rm_accu_list[::-1], 'ppi_mp_p_accu': ppi_mp_p_accu_list[::-1],
                                     'ppi_accu_qt50': ppi_accu_qt50_list,

                                     'm_range': m_range}, safe=False)
            else:
                return HttpResponse(status=404)
        except Exception as err:
            logger.error(err)
            return HttpResponse(status=500)


def get_gdp(request, start_q, end_q):
    if request.method == 'GET':
        pro = ts.pro_api()

        gdp_list = []
        gdp_yoy_list = []
        gdp_qt50_list = []
        gdp_yoy_qt50_list = []
        pi_list = []
        pi_yoy_list = []
        pi_qt50_list = []
        pi_yoy_qt50_list = []
        si_list = []
        si_yoy_list = []
        si_qt50_list = []
        si_yoy_qt50_list = []
        ti_list = []
        ti_yoy_list = []
        ti_qt50_list = []
        ti_yoy_qt50_list = []
        m_range = []
        date_label = []

        try:
            df = pro.cn_gdp(start_q=start_q, end_q=end_q)
            gdp_qt50 = df['gdp'].quantile() if df['gdp'].quantile(
            ) is not None and not np.isnan(df['gdp'].quantile()) else 0
            gdp_yoy_50qt = round(df['gdp_yoy'].quantile(), 2) if df['gdp_yoy'].quantile(
            ) is not None and not np.isnan(df['gdp_yoy'].quantile()) else 0

            pi_qt50 = df['pi'].quantile() if df['pi'].quantile(
            ) is not None and not np.isnan(df['pi'].quantile()) else 0
            pi_yoy_50qt = round(df['pi_yoy'].quantile(), 2) if df['pi_yoy'].quantile(
            ) is not None and not np.isnan(df['pi_yoy'].quantile()) else 0

            si_qt50 = df['si'].quantile() if df['si'].quantile(
            ) is not None and not np.isnan(df['si'].quantile()) else 0
            si_yoy_50qt = round(df['si_yoy'].quantile(), 2) if df['si_yoy'].quantile(
            ) is not None and not np.isnan(df['si_yoy'].quantile()) else 0

            ti_qt50 = df['ti'].quantile() if df['ti'].quantile(
            ) is not None and not np.isnan(df['ti'].quantile()) else 0
            ti_yoy_50qt = round(df['ti_yoy'].quantile(), 2) if df['ti_yoy'].quantile(
            ) is not None and not np.isnan(df['ti_yoy'].quantile()) else 0

            m_range.append(75)
            m_range.append(100)

            if df is not None and len(df) > 0:
                for index, row in df.iterrows():
                    date_label.append(row['quarter'])
                    gdp_list.append(row['gdp']
                                    if row['gdp'] is not None and not np.isnan(row['gdp']) else 0)
                    gdp_yoy_list.append(row['gdp_yoy'] if row['gdp_yoy'] is not None and not np.isnan(
                        row['gdp_yoy']) else 0)
                    gdp_qt50_list.append(gdp_qt50)
                    gdp_yoy_qt50_list.append(gdp_yoy_50qt)

                    pi_list.append(row['pi']
                                   if row['pi'] is not None and not np.isnan(row['pi']) else 0)
                    pi_yoy_list.append(row['pi_yoy'] if row['pi_yoy'] is not None and not np.isnan(
                        row['pi_yoy']) else 0)
                    pi_qt50_list.append(pi_qt50)
                    pi_yoy_qt50_list.append(pi_yoy_50qt)

                    si_list.append(row['si']
                                   if row['si'] is not None and not np.isnan(row['si']) else 0)
                    si_yoy_list.append(row['si_yoy'] if row['si_yoy'] is not None and not np.isnan(
                        row['si_yoy']) else 0)
                    si_qt50_list.append(si_qt50)
                    si_yoy_qt50_list.append(si_yoy_50qt)

                    ti_list.append(row['ti']
                                   if row['ti'] is not None and not np.isnan(row['ti']) else 0)
                    ti_yoy_list.append(row['ti_yoy'] if row['ti_yoy'] is not None and not np.isnan(
                        row['ti_yoy']) else 0)
                    ti_qt50_list.append(ti_qt50)
                    ti_yoy_qt50_list.append(ti_yoy_50qt)

                return JsonResponse({'date_label': date_label[::-1],
                                     'gdp': gdp_list[::-1], 'gdp_yoy': gdp_yoy_list[::-1],
                                     'gdp_qt50': gdp_qt50_list[::-1], 'gdp_yoy_qt50': gdp_yoy_qt50_list[::-1],
                                     'pi': pi_list[::-1], 'pi_yoy': pi_yoy_list[::-1],
                                     'pi_qt50': pi_qt50_list[::-1], 'pi_yoy_qt50': pi_yoy_qt50_list[::-1],
                                     'si': si_list[::-1], 'si_yoy': si_yoy_list[::-1],
                                     'si_qt50': si_qt50_list[::-1], 'si_yoy_qt50': si_yoy_qt50_list[::-1],
                                     'ti': ti_list[::-1], 'gdp_yoy': ti_yoy_list[::-1],
                                     'ti_qt50': ti_qt50_list[::-1], 'ti_yoy_qt50': ti_yoy_qt50_list[::-1],
                                     'm_range': m_range}, safe=False)
            else:
                return HttpResponse(status=404)
        except Exception as err:
            logger.error(err)
            return HttpResponse(status=500)


def get_shibor(request, start_date, end_date):
    if request.method == 'GET':
        pro = ts.pro_api()

        shibor_on_list = []
        shibor_1w_list = []
        shibor_2w_list = []
        shibor_1m_list = []
        shibor_3m_list = []
        shibor_6m_list = []
        shibor_9m_list = []
        shibor_1y_list = []
        m_range = []
        date_label = []

        try:
            df = pro.shibor(start_date=start_date, end_date=end_date)
            m_range.append(75)
            m_range.append(100)

            if df is not None and len(df) > 0:
                for index, row in df.iterrows():
                    date_label.append(row['date'])
                    shibor_on_list.append(row['on']
                                          if row['on'] is not None and not np.isnan(row['on']) else 0)
                    shibor_1w_list.append(row['1w']
                                          if row['1w'] is not None and not np.isnan(row['1w']) else 0)
                    shibor_2w_list.append(row['2w']
                                          if row['2w'] is not None and not np.isnan(row['2w']) else 0)
                    shibor_1m_list.append(row['1m']
                                          if row['1m'] is not None and not np.isnan(row['1m']) else 0)
                    shibor_3m_list.append(row['3m']
                                          if row['3m'] is not None and not np.isnan(row['3m']) else 0)
                    shibor_6m_list.append(row['6m']
                                          if row['6m'] is not None and not np.isnan(row['6m']) else 0)
                    shibor_9m_list.append(row['9m']
                                          if row['9m'] is not None and not np.isnan(row['9m']) else 0)
                    shibor_1y_list.append(row['1y']
                                          if row['1y'] is not None and not np.isnan(row['1y']) else 0)

                return JsonResponse({'date_label': date_label[::-1],
                                     'shibor_on': shibor_on_list[::-1], 'shibor_1w': shibor_1w_list[::-1],
                                     'shibor_2w': shibor_2w_list[::-1], 'shibor_1m': shibor_1m_list[::-1],
                                     'shibor_3m': shibor_3m_list[::-1], 'shibor_6m': shibor_6m_list[::-1],
                                     'shibor_9m': shibor_9m_list[::-1], 'shibor_1y': shibor_1y_list[::-1],
                                     'm_range': m_range}, safe=False)
            else:
                return HttpResponse(status=404)
        except Exception as err:
            logger.error(err)
            return HttpResponse(status=500)


def get_libor(request, start_date, end_date):
    if request.method == 'GET':
        pro = ts.pro_api()

        libor_on_list = []
        libor_1w_list = []
        libor_1m_list = []
        libor_2m_list = []
        libor_3m_list = []
        libor_6m_list = []
        libor_12m_list = []
        m_range = []
        date_label = []

        try:
            df = pro.libor(start_date=start_date, end_date=end_date)
            m_range.append(75)
            m_range.append(100)

            if df is not None and len(df) > 0:
                for index, row in df.iterrows():
                    date_label.append(row['date'])
                    libor_on_list.append(row['on']
                                          if row['on'] is not None and not np.isnan(row['on']) else 0)
                    libor_1w_list.append(row['1w']
                                          if row['1w'] is not None and not np.isnan(row['1w']) else 0)
                    libor_1m_list.append(row['1m']
                                          if row['1m'] is not None and not np.isnan(row['1m']) else 0)
                    libor_2m_list.append(row['2m']
                                          if row['2m'] is not None and not np.isnan(row['2m']) else 0)                      
                    libor_3m_list.append(row['3m']
                                          if row['3m'] is not None and not np.isnan(row['3m']) else 0)
                    libor_6m_list.append(row['6m']
                                          if row['6m'] is not None and not np.isnan(row['6m']) else 0)
                    libor_12m_list.append(row['12m']
                                          if row['12m'] is not None and not np.isnan(row['12m']) else 0)

                return JsonResponse({'date_label': date_label[::-1],
                                     'libor_on': libor_on_list[::-1], 'libor_1w': libor_1w_list[::-1],
                                     'libor_2m': libor_2m_list[::-1], 'libor_1m': libor_1m_list[::-1],
                                     'libor_3m': libor_3m_list[::-1], 'libor_6m': libor_6m_list[::-1],
                                     'libor_12m': libor_12m_list[::-1], 'm_range': m_range}, safe=False)
            else:
                return HttpResponse(status=404)
        except Exception as err:
            logger.error(err)
            return HttpResponse(status=500)


def get_hibor(request, start_date, end_date):
    if request.method == 'GET':
        pro = ts.pro_api()

        hibor_on_list = []
        hibor_1w_list = []
        hibor_1m_list = []
        hibor_2m_list = []
        hibor_3m_list = []
        hibor_6m_list = []
        hibor_12m_list = []
        m_range = []
        date_label = []

        try:
            df = pro.hibor(start_date=start_date, end_date=end_date)
            m_range.append(75)
            m_range.append(100)

            if df is not None and len(df) > 0:
                for index, row in df.iterrows():
                    date_label.append(row['date'])
                    hibor_on_list.append(row['on']
                                          if row['on'] is not None and not np.isnan(row['on']) else 0)
                    hibor_1w_list.append(row['1w']
                                          if row['1w'] is not None and not np.isnan(row['1w']) else 0)
                    hibor_1m_list.append(row['1m']
                                          if row['1m'] is not None and not np.isnan(row['1m']) else 0)
                    hibor_2m_list.append(row['2m']
                                          if row['2m'] is not None and not np.isnan(row['2m']) else 0)                      
                    hibor_3m_list.append(row['3m']
                                          if row['3m'] is not None and not np.isnan(row['3m']) else 0)
                    hibor_6m_list.append(row['6m']
                                          if row['6m'] is not None and not np.isnan(row['6m']) else 0)
                    hibor_12m_list.append(row['12m']
                                          if row['12m'] is not None and not np.isnan(row['12m']) else 0)

                return JsonResponse({'date_label': date_label[::-1],
                                     'hibor_on': hibor_on_list[::-1], 'hibor_1w': hibor_1w_list[::-1],
                                     'hibor_2m': hibor_2m_list[::-1], 'hibor_1m': hibor_1m_list[::-1],
                                     'hibor_3m': hibor_3m_list[::-1], 'hibor_6m': hibor_6m_list[::-1],
                                     'hibor_12m': hibor_12m_list[::-1], 'm_range': m_range}, safe=False)
            else:
                return HttpResponse(status=404)
        except Exception as err:
            logger.error(err)
            return HttpResponse(status=500)


def get_lpr(request, start_date, end_date):
    if request.method == 'GET':
        pro = ts.pro_api()
        shibor_lpr_list = []
        m_range = []
        date_label = []

        try:
            df = pro.shibor_lpr(start_date=start_date, end_date=end_date)
            m_range.append(75)
            m_range.append(100)

            if df is not None and len(df) > 0:
                for index, row in df.iterrows():
                    date_label.append(row['date'])
                    shibor_lpr_list.append(row['1y']
                                          if row['1y'] is not None and not np.isnan(row['1y']) else 0)

                return JsonResponse({'date_label': date_label[::-1],
                                     'shibor_lpr': shibor_lpr_list[::-1],
                                     'm_range': m_range}, safe=False)
            else:
                return HttpResponse(status=404)
        except Exception as err:
            logger.error(err)
            return HttpResponse(status=500)