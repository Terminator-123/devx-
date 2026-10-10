"""
Pydantic schemas for RallyLens AI Backend API.
Member 4: Backend API Lead (Hour 3)
"""

from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"


class MatchUploadResponse(BaseModel):
    match_id: str
    status: str = "uploaded"
    filename: Optional[str] = None


class AnalyzeRequest(BaseModel):
    sport: str = Field(default="badminton", description="Target sport type")
    court_type: str = Field(default="doubles", description="Court type: singles or doubles")
    court_corners: Optional[List[List[float]]] = Field(
        default=None,
        description="4 points in order: top-left, top-right, bottom-right, bottom-left"
    )


class AnalyzeResponse(BaseModel):
    match_id: str
    status: str = "queued"
    message: str = "Analysis queued successfully"


class MatchStatusResponse(BaseModel):
    match_id: str
    status: str  # uploaded | queued | processing | completed | failed
    progress: Optional[float] = None
    error: Optional[str] = None


class MetricItem(BaseModel):
    key: str
    label: str
    value: Any = None
    unit: str
    quality: Optional[str] = "calibrated"
    confidence: Optional[float] = None


class EventItem(BaseModel):
    id: str
    type: str
    start_seconds: float
    end_seconds: float
    title: str
    confidence: Optional[float] = None
    quality: Optional[str] = "observed"
    evidence_url: Optional[str] = None
    coaching_suggestion: Optional[str] = None
    measured_pattern: Optional[str] = None
    evidence_metrics: Optional[str] = None


class TrackSample(BaseModel):
    timestamp_seconds: float
    player_id: int
    bbox_xyxy: List[float]
    footpoint_px: List[float]
    detector_confidence: float
    court_x: Optional[float] = None
    court_y: Optional[float] = None
    calibration_valid: bool = False


class TrackItem(BaseModel):
    player_id: int
    samples: List[TrackSample] = []


class HeatmapCell(BaseModel):
    x: int
    y: int
    count: int


class HeatmapData(BaseModel):
    width: int = 10
    height: int = 5
    cells: List[HeatmapCell] = []


class MediaUrls(BaseModel):
    original_video: str
    annotated_video: Optional[str] = None
    annotated_preview: Optional[str] = None


class AICoachReport(BaseModel):
    tactical_summary: str
    strengths: List[str] = []
    weaknesses: List[str] = []
    actionable_drills: List[str] = []
    fatigue_or_pace_rating: str = "Moderate"
    player_target: str = "Player 1"


class ManualObservationInput(BaseModel):
    timestamp_seconds: float
    player_id: int = 1
    event_type: str = "custom_note" # e.g. "unforced_error", "smash_winner", "poor_recovery", "net_kill"
    notes: str
    court_zone: Optional[str] = "Midcourt" # "Forecourt", "Midcourt", "Rearcourt"


class TrainingDatasetRequest(BaseModel):
    dataset_name: str # e.g. "BFMD", "Shuttlecock Trajectory Dataset", "SportsMOT"
    epochs: int = 10
    batch_size: int = 16
    augment_contrast: bool = True
    target_task: str = "player_and_shuttle" # "player_and_shuttle", "trajectory", "multi_object_tracking"


class TrainingJobStatus(BaseModel):
    job_id: str
    dataset_name: str
    status: str # "queued", "downloading_manifest", "training", "completed"
    progress: float
    current_epoch: int
    total_epochs: int
    current_map50: float
    log_output: str


class MatchResultsResponse(BaseModel):
    match_id: str
    sport: str = "badminton"
    status: str = "completed"
    duration_seconds: float = 0.0
    metrics: List[MetricItem] = []
    events: List[EventItem] = []
    tracks: List[TrackItem] = []
    heatmap: HeatmapData = HeatmapData()
    warnings: List[str] = []
    media_urls: Optional[MediaUrls] = None
    ai_coach: Optional[AICoachReport] = None
    manual_observations: Optional[List[ManualObservationInput]] = []
