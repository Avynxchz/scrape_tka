import sqlite3, os
db = 'data/ai_tutor.db'
if not os.path.exists(db):
    print('DB tidak ada')
else:
    c = sqlite3.connect(db)
    tabs = [r[0] for r in c.execute("select name from sqlite_master where type='table'")]
    print('TABEL:', tabs)
    if 'ai_tutor_users' in tabs:
        print('users     :', c.execute('select count(*) from ai_tutor_users').fetchone()[0])
        for r in c.execute("select user_key, tier, daily_date, daily_count, created_at, updated_at from ai_tutor_users order by updated_at desc limit 10"):
            print('  ', r)
    if 'ai_tutor_conversations' in tabs:
        print('conversations:', c.execute('select count(*) from ai_tutor_conversations').fetchone()[0])
        for r in c.execute("select user_key, subject, paket, created_at from ai_tutor_conversations order by id desc limit 10"):
            print('  ', r)
    if 'feedback' in tabs:
        print('feedback  :', c.execute('select count(*) from feedback').fetchone()[0])
