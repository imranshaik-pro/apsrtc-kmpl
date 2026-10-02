from datetime import date, datetime
from pathlib import Path
from unittest.mock import Mock
import pytest

import run_automated_daily as runner
from src.integrations import google_drive
from test_daily_template import SAMPLE


@pytest.mark.parametrize('existing', [False,True])
def test_html_upload_uses_html_mime_and_only_its_companion_id(tmp_path,monkeypatch,existing):
    source=tmp_path/'PRODDUTUR_2026-09-30.txt';source.write_text(SAMPLE)
    styled=tmp_path/'PRODDUTUR_2026-09-30_daily-v1.html';styled.write_text('<html>report</html>')
    client=Mock();files=client.files.return_value
    response={'id':'HTML','webViewLink':'https://drive.google.com/file/d/HTML/view'}
    files.create.return_value.execute.return_value=response.copy()
    files.update.return_value.execute.return_value=response.copy()
    monkeypatch.setattr(google_drive,'drive_service',lambda:client)
    lookup=[]
    monkeypatch.setattr(google_drive,'find_file',lambda **kwargs:lookup.append(kwargs) or ({'id':'HTML'} if existing else None))
    result=google_drive.upload_daily_html(styled,'FOLDER')
    call=files.update.call_args if existing else files.create.call_args
    assert call.kwargs['media_body'].mimetype()=='text/html'
    assert lookup==[{'folder_id':'FOLDER','filename':styled.name}]
    if existing:
        assert call.kwargs['fileId']=='HTML'
        files.create.assert_not_called()
    else:
        assert call.kwargs['body']=={'name':styled.name,'parents':['FOLDER']}
        files.update.assert_not_called()
    assert result['already_existed']==existing
    assert source.read_text()==SAMPLE


@pytest.mark.parametrize('name',['source.txt','arbitrary.html','PRODDUTUR_2026-09-30.xlsx'])
def test_html_publisher_rejects_unrelated_files(tmp_path,monkeypatch,name):
    monkeypatch.setattr(google_drive,'drive_service',lambda:pytest.fail('Must not contact Drive'))
    with pytest.raises(ValueError):
        google_drive.upload_daily_html(tmp_path/name,'FOLDER')


def test_styled_delivery_emits_the_styled_link_and_preserves_source(tmp_path,monkeypatch,capsys):
    source=tmp_path/'PRODDUTUR_2026-09-30.txt';source.write_text(SAMPLE)
    outputs=[]
    def publish(path,folder_id):
        outputs.append((path,folder_id))
        assert 'daily-template' in path.read_text()
        return {'id':'HTML','webViewLink':'https://drive.google.com/file/d/HTML/view'}
    monkeypatch.setattr(runner,'upload_daily_html',publish)
    runner.publish_styled_report(source,'PRODDUTUR',date(2026,9,30),'https://drive.google.com/file/d/TXT/view','FOLDER',True,True)
    log=capsys.readouterr().out
    assert 'DRIVE_LINK: https://drive.google.com/file/d/HTML/view' in log
    assert 'SOURCE_DRIVE_LINK: https://drive.google.com/file/d/TXT/view' in log
    assert outputs[0][0].name.endswith('_daily-v1_current.html')
    assert source.read_text()==SAMPLE


def test_cached_historical_runner_renders_the_locked_template_without_tyres(tmp_path,monkeypatch,capsys):
    class Clock:
        @classmethod
        def now(cls,tz):return datetime(2026,10,2,10,30,tzinfo=tz)
    monkeypatch.setattr(runner,'datetime',Clock)
    monkeypatch.setattr(runner,'ROOT',tmp_path)
    settings={'daily':{'default_depot':'pdtr','drive_folder_id':'FOLDER'}}
    mapping={'pdtr':{'display_name':'PRODDUTUR','vehicle_depot':'PDTR/PRODDUTUR','region_code':'YSRKADAPA'}}
    monkeypatch.setattr(runner,'load_json',lambda path:settings if path==runner.SETTINGS_PATH else mapping)
    monkeypatch.setattr(runner,'find_file',lambda **kwargs:{'id':'TXT','webViewLink':'https://drive.google.com/file/d/TXT/view'})
    def download(file_id,path):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(SAMPLE)
    monkeypatch.setattr(runner,'download_file',download)
    monkeypatch.setattr(runner,'run_report',lambda **kwargs:pytest.fail('Historical cache must be reused'))
    def publish(path,folder_id):
        assert '🛞' not in path.read_text()
        assert '4.98' in path.read_text()
        return {'id':'HTML','webViewLink':'https://drive.google.com/file/d/HTML/view'}
    monkeypatch.setattr(runner,'upload_daily_html',publish)
    monkeypatch.setattr(runner.sys,'argv',['runner','--depot','pdtr','--date','2026-09-30'])
    assert runner.main()==0
    log=capsys.readouterr().out
    assert 'ALREADY_DELIVERED: https://drive.google.com/file/d/TXT/view' in log
    assert 'DRIVE_LINK: https://drive.google.com/file/d/HTML/view' in log
    assert 'DAILY_TEMPLATE: daily-v1' in log
