ALTER TABLE stories
ADD COLUMN user_id INTEGER;

ALTER TABLE stories
ADD CONSTRAINT fk_stories_user
FOREIGN KEY (user_id)
REFERENCES users(id);