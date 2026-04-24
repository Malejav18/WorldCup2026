// ---- Auth ----
export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface UserPublic {
  id: string;
  email: string;
  role: string;
  created_at: string;
}

// ---- User profile ----
export interface UserProfileSelf {
  id: string;
  email: string;
  display_name: string;
  avatar_url: string | null;
  timezone: string;
  language: string;
  total_points: number;
  global_rank: number | null;
  created_at: string;
  updated_at: string;
}

// ---- Tournament ----
export interface Team {
  id: string;
  name: string;
  country_code: string;
  confederation: string;
  group_id: string | null;
}

export interface Group {
  id: string;
  letter: string;
  name: string;
}

export interface GroupWithTeams extends Group {
  teams: Team[];
}

export interface StandingRow {
  team_id: string;
  team_name: string;
  position: number;
  played: number;
  won: number;
  drawn: number;
  lost: number;
  goals_for: number;
  goals_against: number;
  goal_difference: number;
  points: number;
}

export interface GroupStandings {
  group: Group;
  rows: StandingRow[];
}

export interface Match {
  id: string;
  match_number: number;
  phase: string;
  group_id: string | null;
  home_team_id: string | null;
  away_team_id: string | null;
  home_team_slot: string | null;
  away_team_slot: string | null;
  scheduled_at: string;
  status: string;
  home_goals_90: number | null;
  away_goals_90: number | null;
  went_to_extra_time: boolean;
  went_to_penalties: boolean;
  home_goals_final: number | null;
  away_goals_final: number | null;
  winner_id: string | null;
}

export interface TournamentInfo {
  status: string;
  total_matches: number;
  finished_matches: number;
  next_match: Match | null;
}

// ---- Predictions ----
export interface Prediction {
  id: number;
  user_id: string;
  match_id: string;
  predicted_home_goals_90: number;
  predicted_away_goals_90: number;
  predicted_winner_id: string | null;
  predicted_goes_to_penalties: boolean;
  match_phase: string;
  is_locked: boolean;
  created_at: string;
  updated_at: string;
}

export interface SpecialPrediction {
  id: number;
  user_id: string;
  prediction_type: "CHAMPION" | "RUNNER_UP" | "THIRD_PLACE";
  team_id: string;
  is_locked: boolean;
  created_at: string;
  updated_at: string;
}

// ---- Scoring ----
export interface Score {
  id: number;
  user_id: string;
  match_id: string;
  phase: string;
  reason: string;
  points_base: number;
  points_bonus: number;
  points_total: number;
  is_from_correction: boolean;
  created_at: string;
  updated_at: string;
}

export interface ScoreSummary {
  user_id: string;
  total_points: number;
  scored_matches: number;
}

// ---- Rankings ----
export interface RankingEntry {
  position: number;
  user_id: string;
  display_name: string | null;
  total_points: number;
}

export interface GlobalRankingPage {
  total_users: number;
  page: number;
  page_size: number;
  entries: RankingEntry[];
}

export interface MyPosition {
  user_id: string;
  position: number | null;
  total_points: number;
  total_users: number;
}

// ---- Leagues ----
export interface League {
  id: string;
  name: string;
  description: string | null;
  created_by_user_id: string;
  created_at: string;
}

export interface LeagueDetail extends League {
  member_count: number;
  my_role: "ADMIN" | "MEMBER" | null;
}

export interface LeagueMember {
  user_id: string;
  display_name: string | null;
  role: "ADMIN" | "MEMBER";
  joined_at: string;
}

export interface LeagueMembers {
  league_id: string;
  members: LeagueMember[];
}

export interface LeagueRanking {
  league_id: string;
  league_name: string;
  total_members: number;
  entries: {
    position: number;
    user_id: string;
    display_name: string | null;
    total_points: number;
  }[];
}

// ---- Notifications ----
export interface Notification {
  id: number;
  user_id: string;
  event_type: string;
  channel: "EMAIL" | "PUSH";
  subject: string;
  body: string;
  status: string;
  read_at: string | null;
  created_at: string;
  sent_at: string | null;
}
