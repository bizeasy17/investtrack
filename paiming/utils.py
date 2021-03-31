import pypinyin
 
 
# 不带声调的(style=pypinyin.NORMAL)
def pinyin(word):
    '''
    返回中文拼音（无分隔）
    '''
    s = ''
    for i in pypinyin.pinyin(word, style=pypinyin.NORMAL):
        s += ''.join(i)
    return s

def pinyin_abbrev(text):
    '''
    返回中文输入文本的拼音首字母
    '''
    text_list = []
    first_py_letter = ''
    for i in text:
        text_list.append(i)
    for w in text_list:
        first_py_letter += ''.join(pinyin(w)[0])
    return first_py_letter

def build_board_label(board=[]):
    board.append({
        'name': 'board',
        'value': '',
        'text': '全部',
    })
    board.append({
        'name': 'board',
        'value': 'SHZB',
        'text': '沪市主板',
    })
    board.append({
        'name': 'board',
        'value': 'SZZB',
        'text': '深市主板',
    })
    board.append({
        'name': 'board',
        'value': 'ZXB',
        'text': '中小板',
    })
    board.append({
        'name': 'board',
        'value': 'CYB',
        'text': '创业板',
    })
    board.append({
        'name': 'board',
        'value': 'KCB',
        'text': '科创板',
    })


def build_industry_label(ind=[]):
    ind.append({
        'name': 'industry',
        'value': 'all',
        'text': '全部',
    })
    ind.append({
        'name': 'industry',
        'value': 'computer',
        'text': '计算机',
    })
    ind.append({
        'name': 'industry',
        'value': 'tele',
        'text': '通信',
    })
    ind.append({
        'name': 'industry',
        'value': 'wine',
        'text': '白酒',
    })
    ind.append({
        'name': 'industry',
        'value': 'other',
        'text': '其他',
    })


def build_area_label(area=[]):
    area.append({
        'name': 'area',
        'value': 'all',
        'text': '全部',
    })
    area.append({
        'name': 'area',
        'value': '北京',
        'text': '北京',
    })
    area.append({
        'name': 'area',
        'value': '上海',
        'text': '上海',
    })
    area.append({
        'name': 'area',
        'value': '广州',
        'text': '广州',
    })
    area.append({
        'name': 'area',
        'value': '深圳',
        'text': '深圳',
    })
    area.append({
        'name': 'area',
        'value': '杭州',
        'text': '杭州',
    })


def build_province_label(province=[]):
    province.append({
        'name': 'province',
        'value': 'all',
        'text': '全部',
    })
    province.append({
        'name': 'province',
        'value': 'zhejiang',
        'text': '浙江',
    })
    province.append({
        'name': 'province',
        'value': 'jiangsu',
        'text': '江苏',
    })
    province.append({
        'name': 'province',
        'value': 'guangdong',
        'text': '广东',
    })
    province.append({
        'name': 'province',
        'value': 'shandong',
        'text': '山东',
    })


def build_degree_label(degree=[]):
    degree.append({
        'name': 'degree',
        'value': 'all',
        'text': '全部',
    })
    degree.append({
        'name': 'degree',
        'value': 'phd',
        'text': '博士',
    })
    degree.append({
        'name': 'degree',
        'value': 'master',
        'text': '硕士',
    })
    degree.append({
        'name': 'degree',
        'value': 'bachelor',
        'text': '本科',
    })
    degree.append({
        'name': 'degree',
        'value': 'other',
        'text': '其他',
    })



def build_marketval_label(market_val=[]):
    market_val.append({
        'name': 'marketVal',
        'value': 'all',
        'text': '全部',
    })
    market_val.append({
        'name': 'marketVal',
        'value': '>5000',
        'text': '>5000亿',
    })
    market_val.append({
        'name': 'marketVal',
        'value': '1000-5000',
        'text': '1000-5000亿',
    })
    market_val.append({
        'name': 'marketVal',
        'value': '500-1000',
        'text': '500-1000亿',
    })
    market_val.append({
        'name': 'marketVal',
        'value': '100-500',
        'text': '100-500亿',
    })
    market_val.append({
        'name': 'marketVal',
        'value': '<100',
        'text': '<100亿',
    })
