""" Application Environment """
import os
import sys
import re
from pathlib import Path

class AppDict():
    """ アプリケーション環境を保持するクラス """
    name = ''
    version = ''
    revision = ''
    status = ''
    resource_path = Path(__file__)
    executed_file = Path(__file__)
    data = {}

    def __init__(self):
        """ インスタンス化しての使用は想定しない """
        errmsg = f"{__name__}: Cannot instantiate this class." \
            + "  Use class methods and class variable data <dictionary type>."
        raise NotImplementedError(errmsg)

    @classmethod
    def setup(cls, name, mainfile, version=r'unknown', revision=r'unknown', status=r'Alpha'):
    # def __init__(self, name, mainfile, version=r'unknown', revision=r'unknown', status=r'Alpha'):
        """ 初期化処理
        保持するインスタンス変数は下記
        - name: アプリケーション名(必須)
        - mainfile: アプリケーションの主ファイル名＝scriptファイルやpyinstallerが作成したexeなど(必須)
        - version: アプリケーションのバージョンを表す任意文字列(任意)
        - revision: ビルド番号を特定する任意文字列: SVNのrev、gitのコミット番号など(任意)
        - status: アプリケーションの状態を表す任意文字列: Alpha/Beta/無印=正式版を推奨(任意)
        """
        cls.name = str(name)
        cls.version = str(version)
        # SVNのキーワード置換が使われていればコアのみ抜き出す
        revision = str(revision)
        matches = re.match(r'\$Rev:? *([0-9]+) *\$', revision, flags=re.I)
        cls.revision = revision if not matches else matches.group(1)
        cls.status = str(status)
        # リソースファイル配置先(フルパス)
        #   Script起動の場合は現在地、pyinstaller化済みの場合はzip展開先
        if hasattr(sys, '_MEIPASS'):
            wk = Path(sys._MEIPASS)
        else:
            wk = Path(mainfile).parent
        cls.resource_path = wk.resolve()
        # インタラクティブ実行時の起動本体ファイル
        #   Script起動の場合は .py ファイル、pyinstaller化済みの場合はexeファイル
        wk = Path(sys.executable) if hasattr(sys, 'frozen') \
            else Path(mainfile)
        cls.executed_file = wk.resolve()
        # ユーザが任意に使える辞書領域
        cls.data = dict()

    @classmethod
    def version_string(cls):
        """ Return version string. """
        version_string = f"{cls.version}-{cls.status}(build:{cls.revision})"
        return version_string

    @classmethod
    def basename(cls):
        """ Return basename of myself == this application. (STRING)"""
        basename = cls.executed_file.name.split('.')[0]
        return basename

    @classmethod
    def wkfile(cls, substr=r'', suffix=r'tmp'):
        """ Return full path of wkfile. (Path object) """
        ##TODO: Check & convert substr which MUST be contained printable chars only.
        wkfile = cls.executed_file.with_name(f'{cls.basename()}{substr}.{suffix}')
        return wkfile

    @classmethod
    def logfile(cls):
        """ Return full path of logfile. (Path object) """
        logfile = cls.executed_file.with_name(f'{cls.basename()}.log')
        return logfile

    @classmethod
    def dump(cls):
        print(
            f"name=<{cls.name}>, status=<{cls.status}>\n"
            + f"version=<{cls.version}>, revision=<{cls.revision}>"
        )
        print(cls.resource_path)
        print(cls.executed_file)
        print(cls.data)



if __name__ == "__main__":
    AppDict.setup('AppDictTest', __file__, 3.5, 1629, 'β')
    AppDict.dump()
    # print(appenv.version_string())
    # print(appenv.basename())
    # print(appenv.wkfile())
    # print(appenv.wkfile(r'_dummy'))
    # print(appenv.logfile())
    AppDict.data['help'] = {'string': 'help string', 'array': ['help','string','array']}
    AppDict.dump()
    import pprint
    print(type(AppDict.data))
    data_str = pprint.pformat(AppDict.data)
    print(data_str)
    pprint.pprint(AppDict.data, width=66)


    # try:
    #     print('instantiate')
    #     ad = AppDict()
    #     print('call classmethod')
    #     ad.dump()
    # except (TypeError,NotImplementedError) as e:
    #     print(type(e))
    #     print(e.args)
    # except Exception as e:
    #     print(type(e))
