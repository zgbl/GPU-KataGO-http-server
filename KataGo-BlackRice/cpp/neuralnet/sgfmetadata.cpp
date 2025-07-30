#include "../neuralnet/sgfmetadata.h"

//------------------------
#include "../core/using.h"
//------------------------

bool SGFMetadata::operator==(const SGFMetadata& other) const {
  return (
    initialized == other.initialized &&
    inverseBRank == other.inverseBRank &&
    inverseWRank == other.inverseWRank &&
    bIsUnranked == other.bIsUnranked &&
    wIsUnranked == other.wIsUnranked &&
    bRankIsUnknown == other.bRankIsUnknown &&
    wRankIsUnknown == other.wRankIsUnknown &&
    bIsHuman == other.bIsHuman &&
    wIsHuman == other.wIsHuman &&
    gameIsUnrated == other.gameIsUnrated &&
    gameRatednessIsUnknown == other.gameRatednessIsUnknown &&

    tcIsUnknown == other.tcIsUnknown &&
    tcIsNone == other.tcIsNone &&
    tcIsAbsolute == other.tcIsAbsolute &&
    tcIsSimple == other.tcIsSimple &&
    tcIsByoYomi == other.tcIsByoYomi &&
    tcIsCanadian == other.tcIsCanadian &&
    tcIsFischer == other.tcIsFischer &&

    mainTimeSeconds == other.mainTimeSeconds &&
    periodTimeSeconds == other.periodTimeSeconds &&
    byoYomiPeriods == other.byoYomiPeriods &&
    canadianMoves == other.canadianMoves &&

    gameDate == other.gameDate &&

    source == other.source
  );
}
bool SGFMetadata::operator!=(const SGFMetadata& other) const {
  return !(*this == other);
}

Hash128 SGFMetadata::getHash(Player nextPlayer) const {
  if(
    !initialized ||
    inverseBRank < 0 ||
    inverseBRank >= 128 ||
    inverseWRank < 0 ||
    inverseWRank >= 128 ||
    source < 0 ||
    source >= 128 ||
    mainTimeSeconds < 0 ||
    periodTimeSeconds < 0 ||
    byoYomiPeriods < 0 ||
    canadianMoves < 0
  ) {
    Global::fatalError("Invalid or uninitialized SGFMetadata for hash");
  }

  uint32_t b =
    (uint32_t)inverseBRank +
    (uint32_t)bIsUnranked * 128u +
    (uint32_t)bRankIsUnknown * 256u +
    (uint32_t)bIsHuman * 512u;
  uint32_t w =
    (uint32_t)inverseWRank +
    (uint32_t)wIsUnranked * 128u +
    (uint32_t)wRankIsUnknown * 256u +
    (uint32_t)wIsHuman * 512u;

  uint32_t x0 = 0;
  uint32_t x1 = 0;
  uint32_t x2 = 0;
  uint32_t x3 = 0;

  if(nextPlayer == P_BLACK)
    x0 += b + (w << 10);
  else
    x0 += w + (b << 10);

  x0 += (uint32_t)gameIsUnrated << 20;
  x0 += (uint32_t)gameRatednessIsUnknown << 21;

  uint32_t whichTC = 0;
  if(tcIsUnknown)
    whichTC = 1;
  else if(tcIsNone)
    whichTC = 2;
  else if(tcIsAbsolute)
    whichTC = 3;
  else if(tcIsSimple)
    whichTC = 4;
  else if(tcIsByoYomi)
    whichTC = 5;
  else if(tcIsCanadian)
    whichTC = 6;
  else if(tcIsFischer)
    whichTC = 7;

  x0 += (uint32_t)whichTC << 22;
  // 7 bits left for source going up to 128
  x0 += (uint32_t)source << 25;

  assert(std::isfinite(mainTimeSeconds));
  assert(std::isfinite(periodTimeSeconds));
  double mainTimeSecondsCapped = std::min(std::max(mainTimeSeconds,0.0),3.0*86400);
  // ~20 bits
  x1 += (uint32_t)(mainTimeSecondsCapped * 4);
  double periodTimeSecondsCapped = std::min(std::max(periodTimeSeconds,0.0),1.0*86400);
  // ~22 bits
  x2 += (uint32_t)(periodTimeSecondsCapped * 32);

  int byoYomiPeriodsCapped = std::min(std::max(byoYomiPeriods,0),50);
  x1 += (uint32_t)byoYomiPeriodsCapped << 24;
  int canadianMovesCapped = std::min(std::max(canadianMoves,0),50);
  x2 += (uint32_t)canadianMovesCapped << 24;

  int daysDifference = gameDate.numDaysAfter(SimpleDate(1970,1,1));
  x3 += (uint32_t)daysDifference;

  uint64_t h0 = Hash::combine(x0,x1);
  uint64_t h1 = Hash::combine(x2,x3);
  h0 = Hash::nasam(h0);
  h1 += h0;
  h1 = Hash::nasam(h1);
  h0 += h1;

  return Hash128(h0,h1);
}


void SGFMetadata::fillMetadataRow(const SGFMetadata* sgfMeta, float* rowMetadata, Player nextPlayer, int boardArea) {
  assert(sgfMeta != NULL);
  if(!sgfMeta->initialized)
    Global::fatalError("Invalid or uninitialized SGFMetadata");

  for(int i = 0; i<SGFMetadata::METADATA_INPUT_NUM_CHANNELS; i++)
    rowMetadata[i] = 0.0f;

  bool plaIsHuman = (nextPlayer == P_WHITE) ? sgfMeta->wIsHuman : sgfMeta->bIsHuman;
  bool oppIsHuman = (nextPlayer == P_WHITE) ? sgfMeta->bIsHuman : sgfMeta->wIsHuman;
  rowMetadata[0] = plaIsHuman ? 1.0f : 0.0f;
  rowMetadata[1] = oppIsHuman ? 1.0f : 0.0f;

  bool plaIsUnranked = (nextPlayer == P_WHITE) ? sgfMeta->wIsUnranked : sgfMeta->bIsUnranked;
  bool oppIsUnranked = (nextPlayer == P_WHITE) ? sgfMeta->bIsUnranked : sgfMeta->wIsUnranked;
  rowMetadata[2] = plaIsUnranked ? 1.0f : 0.0f;
  rowMetadata[3] = oppIsUnranked ? 1.0f : 0.0f;

  bool plaRankIsUnknown = (nextPlayer == P_WHITE) ? sgfMeta->wRankIsUnknown : sgfMeta->bRankIsUnknown;
  bool oppRankIsUnknown = (nextPlayer == P_WHITE) ? sgfMeta->bRankIsUnknown : sgfMeta->wRankIsUnknown;
  rowMetadata[4] = plaRankIsUnknown ? 1.0f : 0.0f;
  rowMetadata[5] = oppRankIsUnknown ? 1.0f : 0.0f;

  static constexpr int RANK_START_IDX = 6;
  int invPlaRank = (nextPlayer == P_WHITE) ? sgfMeta->inverseWRank : sgfMeta->inverseBRank;
  int invOppRank = (nextPlayer == P_WHITE) ? sgfMeta->inverseBRank : sgfMeta->inverseWRank;
  static constexpr int RANK_LEN_PER_PLA = 34;
  if(!plaIsUnranked) {
    for(int i = 0; i<std::min(invPlaRank,RANK_LEN_PER_PLA); i++)
      rowMetadata[RANK_START_IDX + i] = 1.0f;
  }
  if(!oppIsUnranked) {
    for(int i = 0; i<std::min(invOppRank,RANK_LEN_PER_PLA); i++)
      rowMetadata[RANK_START_IDX + RANK_LEN_PER_PLA + i] = 1.0f;
  }

  static_assert(74 == RANK_START_IDX + 2 * RANK_LEN_PER_PLA, "");
  rowMetadata[74] = sgfMeta->gameRatednessIsUnknown ? 0.5f : sgfMeta->gameIsUnrated ? 1.0f : 0.0f;

  rowMetadata[75] = sgfMeta->tcIsUnknown ? 1.0f : 0.0f;
  rowMetadata[76] = sgfMeta->tcIsNone ? 1.0f : 0.0f;
  rowMetadata[77] = sgfMeta->tcIsAbsolute ? 1.0f : 0.0f;
  rowMetadata[78] = sgfMeta->tcIsSimple ? 1.0f : 0.0f;
  rowMetadata[79] = sgfMeta->tcIsByoYomi ? 1.0f : 0.0f;
  rowMetadata[80] = sgfMeta->tcIsCanadian ? 1.0f : 0.0f;
  rowMetadata[81] = sgfMeta->tcIsFischer ? 1.0f : 0.0f;
  assert(rowMetadata[75] + rowMetadata[76] + rowMetadata[77] + rowMetadata[78] + rowMetadata[79] + rowMetadata[80] + rowMetadata[81] == 1.0f);

  double mainTimeSecondsCapped = std::min(std::max(sgfMeta->mainTimeSeconds,0.0),3.0*86400);
  double periodTimeSecondsCapped = std::min(std::max(sgfMeta->periodTimeSeconds,0.0),1.0*86400);
  rowMetadata[82] = (float)(0.4 * (log(mainTimeSecondsCapped + 60.0) - 6.5));
  rowMetadata[83] = (float)(0.3 * (log(periodTimeSecondsCapped + 1.0) - 3.0));
  int byoYomiPeriodsCapped = std::min(std::max(sgfMeta->byoYomiPeriods,0),50);
  int canadianMovesCapped = std::min(std::max(sgfMeta->canadianMoves,0),50);
  rowMetadata[84] = (float)(0.5 * (log(byoYomiPeriodsCapped + 2.0) - 1.5));
  rowMetadata[85] = (float)(0.25 * (log(canadianMovesCapped + 2.0) - 1.5));

  rowMetadata[86] = (float)(0.5 * log(boardArea/361.0));

  double daysDifference = sgfMeta->gameDate.numDaysAfter(SimpleDate(1970,1,1));
  static constexpr int DATE_START_IDX = 87;
  static constexpr int DATE_LEN = 32;
  // 7 because we're curious if there's a day-of-the-week effect
  // on gameplay...
  double period = 7.0;
  static const double factor = pow(80000, 1.0/(DATE_LEN-1));
  static constexpr double twopi = 6.283185307179586476925;
  for(int i = 0; i<DATE_LEN; i++) {
    double numRevolutions = daysDifference / period;
    rowMetadata[DATE_START_IDX + i*2 + 0] = (float)(cos(numRevolutions * twopi));
    rowMetadata[DATE_START_IDX + i*2 + 1] = (float)(sin(numRevolutions * twopi));
    period *= factor;
  }
  static_assert(151 == DATE_START_IDX + 2 * DATE_LEN, "");

  assert(sgfMeta->source >= 0 && sgfMeta->source < 16);
  rowMetadata[151 + sgfMeta->source] = 1.0f;

  static_assert(151 + 16 < SGFMetadata::METADATA_INPUT_NUM_CHANNELS, "");
}

static SGFMetadata makeBasicRankProfile(int inverseRankBlack, int inverseRankWhite, bool preAZ) {
  // KGS rating system is pretty reasonable, so let's use KGS as the source.
  SGFMetadata ret;
  ret.initialized = true;
  ret.inverseBRank = inverseRankBlack;
  ret.inverseWRank = inverseRankWhite;
  ret.bIsHuman = true;
  ret.wIsHuman = true;
  ret.gameRatednessIsUnknown = true;
  ret.tcIsByoYomi = true;
  ret.mainTimeSeconds = 1200;
  ret.periodTimeSeconds = 30;
  ret.byoYomiPeriods = 5;
  if(preAZ)
    ret.gameDate = SimpleDate(2016,9,1);
  else
    ret.gameDate = SimpleDate(2020,3,1);
  ret.source = SGFMetadata::SOURCE_KGS;
  return ret;
}

static SGFMetadata makeHistoricalProProfile(SimpleDate date) {
  SGFMetadata ret;
  ret.initialized = true;
  ret.inverseBRank = 1;
  ret.inverseWRank = 1;
  ret.bIsHuman = true;
  ret.wIsHuman = true;
  ret.tcIsUnknown = true;
  ret.gameDate = date;
  ret.source = SGFMetadata::SOURCE_GOGOD;
  return ret;
}

static SGFMetadata makeModernProProfile(SimpleDate date) {
  SGFMetadata ret;
  ret.initialized = true;
  ret.inverseBRank = 1;
  ret.inverseWRank = 1;
  ret.bIsHuman = true;
  ret.wIsHuman = true;
  ret.tcIsUnknown = true;
  ret.gameDate = date;
  ret.source = SGFMetadata::SOURCE_GO4GO;
  return ret;
}

SGFMetadata SGFMetadata::getProfile(const string& humanSLProfileName) {
  if(humanSLProfileName == "" || humanSLProfileName == "_" || humanSLProfileName == "\"\"")
    return SGFMetadata();

  if(Global::isPrefix(humanSLProfileName,"proyear_")) {
    string yearStr = Global::chopPrefix(humanSLProfileName,"proyear_");
    int year;
    bool suc = Global::tryStringToInt(yearStr,year);
    if(suc && year >= 1800 && year <= 2020) {
      return makeHistoricalProProfile(SimpleDate(year,6,1));
    }
    if(suc && year >= 2021 && year <= 2023) {
      return makeModernProProfile(SimpleDate(year,6,1));
    }
  }
  if(Global::isPrefix(humanSLProfileName,"rank_") || Global::isPrefix(humanSLProfileName,"preaz_")) {
    string ranksStr;
    bool preAZ;
    if(Global::isPrefix(humanSLProfileName,"rank_")) {
      ranksStr = Global::chopPrefix(humanSLProfileName,"rank_");
      preAZ = false;
    }
    else {
      ranksStr = Global::chopPrefix(humanSLProfileName,"preaz_");
      preAZ = true;
    }

    auto getInverseRank = [](const string& rankStr) {
      if(rankStr == "9d") return 1;
      if(rankStr == "8d") return 2;
      if(rankStr == "7d") return 3;
      if(rankStr == "6d") return 4;
      if(rankStr == "5d") return 5;
      if(rankStr == "4d") return 6;
      if(rankStr == "3d") return 7;
      if(rankStr == "2d") return 8;
      if(rankStr == "1d") return 9;
      if(rankStr == "1k") return 10;
      if(rankStr == "2k") return 11;
      if(rankStr == "3k") return 12;
      if(rankStr == "4k") return 13;
      if(rankStr == "5k") return 14;
      if(rankStr == "6k") return 15;
      if(rankStr == "7k") return 16;
      if(rankStr == "8k") return 17;
      if(rankStr == "9k") return 18;
      if(rankStr == "10k") return 19;
      if(rankStr == "11k") return 20;
      if(rankStr == "12k") return 21;
      if(rankStr == "13k") return 22;
      if(rankStr == "14k") return 23;
      if(rankStr == "15k") return 24;
      if(rankStr == "16k") return 25;
      if(rankStr == "17k") return 26;
      if(rankStr == "18k") return 27;
      if(rankStr == "19k") return 28;
      if(rankStr == "20k") return 29;
      return -1;
    };

    int inverseRank = getInverseRank(ranksStr);
    if(inverseRank != -1)
      return makeBasicRankProfile(inverseRank,inverseRank,preAZ);

    std::vector<std::string> pieces = Global::split(ranksStr,'_');
    if(pieces.size() == 2) {
      int inverseRankBlack = getInverseRank(pieces[0]);
      int inverseRankWhite = getInverseRank(pieces[1]);
      if(inverseRankBlack != -1 && inverseRankWhite != -1) {
        return makeBasicRankProfile(inverseRankBlack,inverseRankWhite,preAZ);
      }
    }
  }

  throw StringError("Unknown human SL network profile: " + humanSLProfileName);
}

