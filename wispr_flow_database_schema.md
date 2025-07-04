# Wispr Flow Database Schema Analysis

## Database Location
`/Users/pedram/Library/Application Support/Wispr Flow/flow.sqlite`

## Database Overview
- **Primary Database**: `flow.sqlite` (main application database)
- **Backup Files**: `backup-2025-07-03T17-00-00.059Z.sqlite` (automated backups)
- **Related Files**: `SharedStorage`, `SharedStorage-wal`, `config.json`

## Tables Overview

### 1. History Table (395 records)
**Purpose**: Main table storing speech-to-text transcription history and metadata

**Key Fields**:
- `transcriptEntityId` (VARCHAR(36), PRIMARY KEY): Unique identifier for each transcription
- `asrText` (TEXT): Original ASR (Automatic Speech Recognition) text
- `formattedText` (TEXT): AI-formatted version of the ASR text
- `editedText` (TEXT): User-edited version of the text
- `timestamp` (DATETIME): When the transcription was created
- `audio` (BLOB): Audio recording data
- `screenshot` (BLOB): Screenshot data
- `additionalContext` (JSON): Contextual information including user data, accessibility context
- `status` (VARCHAR(255)): Processing status (formatted, empty, extension_other, etc.)
- `app` (VARCHAR(255)): Application where transcription was used
- `url` (VARCHAR(255)): URL if applicable
- `e2eLatency` (FLOAT): End-to-end latency measurement
- `duration` (FLOAT): Recording duration in seconds
- `numWords` (INTEGER): Word count
- `shareType` (TEXT): Sharing configuration
- `language` (TEXT): Detected/specified language
- `isArchived` (TINYINT(1)): Archive flag
- `conversationId` (VARCHAR(255)): Conversation grouping identifier

**Advanced Fields**:
- `toneMatchedText` (TEXT): Tone-adjusted text
- `toneMatchPairs` (JSONB): Tone matching data
- `feedback` (TEXT): User feedback
- `micDevice` (TEXT): Microphone device used
- `formattingDivergenceScore` (FLOAT): Quality metrics
- `fallbackAsrText`, `fallbackFormattedText` (TEXT): Fallback processing results
- `averageLogProb` (FLOAT): Confidence metrics
- `axText`, `axHTML` (TEXT): Accessibility text extraction
- `userEditMetaData` (JSON): Edit tracking metadata
- `opusChunks` (JSON): Audio chunk information

**Indexes**:
- `idx_formattedText` ON `formattedText`
- `idx_timestamp_archived` ON `timestamp`, `isArchived`
- `idx_duration_numWords` ON `numWords`, `duration`
- `idx_editedtextstatus_conversationid_timestamp_app_url` ON multiple fields

### 2. Dictionary Table (23 records)
**Purpose**: Custom dictionary for user-specific terms and corrections

**Fields**:
- `phrase` (VARCHAR(255), PRIMARY KEY): The dictionary entry
- `lastUsed` (DATETIME): When the phrase was last used
- `lastSeen` (DATETIME): When the phrase was last seen
- `frequencyUsed` (INTEGER): Usage frequency counter
- `frequencySeen` (INTEGER): Seen frequency counter
- `manualEntry` (TINYINT(1)): Whether manually added by user
- `source` (TEXT): Source of the entry (manual, user_edits)
- `replacement` (VARCHAR(255)): Replacement text if applicable
- `id` (VARCHAR(36)): Unique identifier
- `createdAt`, `modifiedAt` (DATETIME): Timestamps
- `isDeleted` (TINYINT(1)): Soft delete flag

### 3. RemoteNotifications Table (0 records)
**Purpose**: Push notifications from remote services

**Fields**:
- `id` (VARCHAR(36), PRIMARY KEY): Notification ID
- `type`, `key` (VARCHAR(255)): Notification categorization
- `title` (VARCHAR(255)): Notification title
- `text` (TEXT): Notification content
- `isArchived`, `isRead` (TINYINT(1)): Status flags
- `createdAt`, `updatedAt` (DATETIME): Timestamps
- `synced` (TINYINT(1)): Sync status

### 4. Notes Table (0 records)
**Purpose**: User notes storage

**Fields**:
- `id` (VARCHAR(36), PRIMARY KEY): Note ID
- `title` (VARCHAR(255)): Note title
- `contentPreview` (TEXT): Preview text
- `content` (TEXT): Full note content
- `createdAt`, `modifiedAt` (DATETIME): Timestamps
- `synced` (TINYINT(1)): Sync status
- `isDeleted` (TINYINT(1)): Soft delete flag

### 5. SequelizeMeta Table
**Purpose**: Database migration tracking (Sequelize ORM)

## Usage Statistics

### Most Active Applications:
1. Slack (`com.tinyspeck.slackmacgap`) - 109 records
2. Obsidian (`md.obsidian`) - 58 records
3. (Unknown/blank) - 55 records
4. Messages (`com.apple.MobileSMS`) - 48 records
5. VS Code (`com.microsoft.VSCode`) - 39 records
6. Chrome (`com.google.Chrome`) - 26 records
7. Wispr Flow (`com.electron.wispr-flow`) - 12 records
8. ChatGPT (`com.openai.chat`) - 10 records

### Status Distribution:
- `formatted`: 306 records (77.5%)
- (blank): 46 records (11.6%)
- `empty`: 18 records (4.6%)
- `extension_other`: 11 records (2.8%)
- `no_audio`: 8 records (2.0%)
- `extension_paste`: 5 records (1.3%)
- `dismissed`: 1 record (0.3%)

## Sample Queries

### Recent Transcriptions
```sql
SELECT 
    transcriptEntityId,
    asrText,
    formattedText,
    timestamp,
    app,
    duration,
    numWords,
    status
FROM History 
WHERE isArchived = 0 
ORDER BY timestamp DESC 
LIMIT 10;
```

### Application Usage Analysis
```sql
SELECT 
    app,
    COUNT(*) as total_uses,
    AVG(duration) as avg_duration,
    AVG(numWords) as avg_words,
    AVG(e2eLatency) as avg_latency
FROM History 
WHERE app IS NOT NULL 
GROUP BY app 
ORDER BY total_uses DESC;
```

### Dictionary Usage
```sql
SELECT 
    phrase,
    frequencyUsed,
    manualEntry,
    source,
    lastUsed
FROM Dictionary 
ORDER BY frequencyUsed DESC, lastUsed DESC;
```

### Daily Activity
```sql
SELECT 
    DATE(timestamp) as date,
    COUNT(*) as transcriptions,
    SUM(duration) as total_duration,
    SUM(numWords) as total_words
FROM History 
GROUP BY DATE(timestamp) 
ORDER BY date DESC;
```

### Quality Metrics
```sql
SELECT 
    status,
    COUNT(*) as count,
    AVG(formattingDivergenceScore) as avg_formatting_score,
    AVG(averageLogProb) as avg_confidence
FROM History 
WHERE status = 'formatted'
GROUP BY status;
```

### Text Processing Pipeline Analysis
```sql
SELECT 
    COUNT(*) as total,
    COUNT(CASE WHEN asrText IS NOT NULL THEN 1 END) as has_asr,
    COUNT(CASE WHEN formattedText IS NOT NULL THEN 1 END) as has_formatted,
    COUNT(CASE WHEN editedText IS NOT NULL THEN 1 END) as has_edited,
    COUNT(CASE WHEN usedFallbackAsr = 1 THEN 1 END) as used_fallback_asr,
    COUNT(CASE WHEN usedFallbackFormatting = 1 THEN 1 END) as used_fallback_formatting
FROM History;
```

## Data Insights

### Audio Processing Pipeline
1. **ASR Stage**: Raw audio → `asrText` (speech recognition)
2. **Formatting Stage**: `asrText` → `formattedText` (AI formatting)
3. **Editing Stage**: `formattedText` → `editedText` (user edits)
4. **Fallback System**: Alternative ASR/formatting when primary fails

### Context Awareness
- **Accessibility Integration**: `axText`, `axHTML` for screen reader context
- **Application Context**: Active app, URL, textbox contents
- **User Context**: Name, email, conversation history
- **Visual Context**: Screenshots, OCR results

### Quality Assurance
- **Confidence Scoring**: `averageLogProb` for ASR confidence
- **Divergence Metrics**: Score differences between processing stages
- **Latency Tracking**: End-to-end processing time measurement

### Privacy Considerations
- Audio data stored as BLOBs in database
- Screenshots captured and stored
- User personal information in context data
- Conversation tracking across sessions

## Technical Notes

- **Database Engine**: SQLite with Sequelize ORM
- **JSON Support**: Both JSON and JSONB column types used
- **Soft Deletes**: `isDeleted` flags instead of hard deletes
- **Sync Architecture**: `synced` flags suggest cloud synchronization
- **Backup Strategy**: Automated timestamped backups in `backups/` directory
- **Performance**: Strategic indexing on frequently queried columns