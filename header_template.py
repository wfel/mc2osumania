template = """osu file format v14

[General]
AudioFilename: {audio_name}
AudioLeadIn: {offset}
PreviewTime: {preview}
Countdown: 0
SampleSet: Soft
StackLeniency: 0.7
Mode:3
LetterboxInBreaks: 0
SpecialStyle: 0
WidescreenStoryboard: 0

[Editor]
DistanceSpacing: 1.6
BeatDivisor: 4
GridSize: 4
TimelineZoom: 2.2

[Metadata]
Title:{title_ascii}
TitleUnicode:{title_unicode}
Artist:{artist_ascii}
ArtistUnicode:{artist_unicode}
Creator:osu_mapper
Version:{version}
Source:null
Tags:null
BeatmapID:0
BeatmapSetID:-1

[Difficulty]
HPDrainRate:8.8
CircleSize:{col_num}
OverallDifficulty:7.0
ApproachRate:5.0
SliderMultiplier:1.0
SliderTickRate:1

[Events]
//Background and Video events
0,0,"{bk}",0,0
//Break Periods
//Storyboard Layer 0 (Background)
//Storyboard Layer 1 (Fail)
//Storyboard Layer 2 (Pass)
//Storyboard Layer 3 (Foreground)
//Storyboard Layer 4 (Overlay)
//Storyboard Sound Samples

[TimingPoints]
{timing_points}


[HitObjects]
{hit_objects}
"""
