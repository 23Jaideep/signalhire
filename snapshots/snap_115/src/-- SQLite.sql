-- SQLite
SELECT candidate_id, COUNT(*) 
FROM sessions 
GROUP BY candidate_id;
SELECT start_time, summary 
FROM sessions
WHERE candidate_id = 'test_user_1'
ORDER BY start_time;
SELECT candidate_id, COUNT(*) as sessions
FROM sessions
GROUP BY candidate_id;
DELETE FROM events
WHERE session_id IN (
    SELECT session_id FROM sessions
    WHERE candidate_id = 'test_user_1'
);
DELETE FROM sessions
WHERE candidate_id = 'test_user_1';
DELETE FROM candidates
WHERE candidate_id = 'test_user_1';
SELECT * FROM candidates;
SELECT * FROM sessions;
SELECT * FROM events;