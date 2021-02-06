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
