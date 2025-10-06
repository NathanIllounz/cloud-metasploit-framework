import sqlite3, os, json, datetime
DB_PATH = os.environ.get('CMF_JOBS_DB', 'jobs.db')

def init_db(db_path=None):
    path = db_path or DB_PATH
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS jobs
                 (job_id TEXT PRIMARY KEY, timestamp TEXT, params TEXT, mode TEXT, status TEXT, exit_code INTEGER, output TEXT)''')
    conn.commit()
    conn.close()
    return path

def create_job(job_id: str, params: dict, mode: str, status: str='pending', exit_code: int=None, output: str=''):
    path = init_db()
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO jobs (job_id,timestamp,params,mode,status,exit_code,output) VALUES (?,?,?,?,?,?,?)',
              (job_id, datetime.datetime.utcnow().isoformat(), json.dumps(params), mode, status, exit_code or 0, output))
    conn.commit()
    conn.close()

def update_job_output(job_id: str, status: str, exit_code: int, output: str):
    path = init_db()
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute('UPDATE jobs SET status=?, exit_code=?, output=? WHERE job_id=?', (status, exit_code, output, job_id))
    conn.commit()
    conn.close()

def get_job(job_id: str):
    path = init_db()
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute('SELECT job_id,timestamp,params,mode,status,exit_code,output FROM jobs WHERE job_id=?', (job_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    return {
        'job_id': row[0],
        'timestamp': row[1],
        'params': json.loads(row[2]),
        'mode': row[3],
        'status': row[4],
        'exit_code': row[5],
        'output': row[6]
    }
