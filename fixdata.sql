-- 1. 删除错误数据
delete from public.analysis_stockhistorydaily where trade_date > '2020-11-19'
-- 2. 删除event log下载和mark_cp日志
delete from public.analysis_analysiseventlog where exec_date > '2020-11-20'
-- 3. 删除straetegy test log下载和mark_cp日志 2020-11-21 ~ 2020-11-23
delete from public.analysis_stockstrategytestlog where start_date = '2020-11-24' and end_date = '2020-11-24'
-- 4. 更新straetegy test log下载，mark_cp的enddate为2020-11-19， created_time < 2020-11-23
update public.analysis_stockstrategytestlog set end_date='2020-11-19' where end_date='2020-11-24'
-- 5. 更新straetegy test log下载，mark_cp的enddate为2020-11-19， created_time < 2020-11-23
update public.analysis_stockstrategytestlog set end_date='2020-11-19' where event_type='HIST_DOWNLOAD' and end_date='2020-11-23'
update public.analysis_stockstrategytestlog set end_date='2020-11-19' where event_type='HIST_DOWNLOAD' and end_date='2020-11-20'


-- 清理历史数据
-- 1. 清理public.analysis_stockhistorydaily
delete from public.analysis_stockhistorydaily
-- 2. 清理public.analysis_stockstrategytestlog
delete from public.analysis_stockstrategytestlog
-- 3. 清理public.analysis_analysiseventlog 
delete from public.analysis_analysiseventlog 
