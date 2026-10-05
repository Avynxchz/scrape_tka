import React from 'react';
import { Audio, interpolate, Sequence, staticFile } from 'remotion';
import { clamp, DUR } from './lib';

export const AudioLayer: React.FC = () => {
  // Background music volume automation with subtle ducking and smooth fades
  const bgmVolume = (f: number) => {
    // Fade-in on entry
    if (f < 24) return interpolate(f, [0, 24], [0, 0.40], clamp);
    // Subtle ducking during wrong answer shake/thud
    if (f >= 230 && f <= 256) return interpolate(f, [230, 234, 246, 256], [0.40, 0.28, 0.28, 0.40], clamp);
    // Subtle ducking during success celebration chime
    if (f >= 518 && f <= 545) return interpolate(f, [518, 522, 536, 545], [0.40, 0.28, 0.28, 0.40], clamp);
    // Fade-out during outro resolve
    if (f > 675) return interpolate(f, [675, DUR - 2], [0.40, 0], clamp);
    return 0.40;
  };

  return (
    <>
      {/* Background Music: Tech Live (Kevin MacLeod, CC BY 4.0) */}
      <Audio src={staticFile('audio/bgm.mp3')} volume={bgmVolume} />

      {/* 0–2s: Hook & Phone Entry */}
      <Sequence from={3} durationInFrames={25}>
        <Audio src={staticFile('audio/sfx_whoosh_enter.wav')} volume={0.45} />
      </Sequence>

      {/* 2–5.5s: Dashboard & Subject Select */}
      <Sequence from={96} durationInFrames={15}>
        <Audio src={staticFile('audio/sfx_card_lift.wav')} volume={0.40} />
      </Sequence>
      <Sequence from={132} durationInFrames={10}>
        <Audio src={staticFile('audio/sfx_tap.wav')} volume={0.50} />
      </Sequence>

      {/* 5.5–9s: Question & Wrong Feedback Shake */}
      <Sequence from={165} durationInFrames={15}>
        <Audio src={staticFile('audio/sfx_slide.wav')} volume={0.35} />
      </Sequence>
      <Sequence from={216} durationInFrames={10}>
        <Audio src={staticFile('audio/sfx_tap.wav')} volume={0.48} />
      </Sequence>
      <Sequence from={230} durationInFrames={10}>
        <Audio src={staticFile('audio/sfx_tap.wav')} volume={0.50} />
      </Sequence>
      <Sequence from={234} durationInFrames={20}>
        <Audio src={staticFile('audio/sfx_error_shake.wav')} volume={0.70} />
      </Sequence>

      {/* 9–11.5s: Explanation & Open AI Tutor */}
      <Sequence from={270} durationInFrames={15}>
        <Audio src={staticFile('audio/sfx_slide.wav')} volume={0.38} />
      </Sequence>
      <Sequence from={308} durationInFrames={10}>
        <Audio src={staticFile('audio/sfx_tap.wav')} volume={0.45} />
      </Sequence>
      <Sequence from={324} durationInFrames={15}>
        <Audio src={staticFile('audio/sfx_drawer_open.wav')} volume={0.50} />
      </Sequence>

      {/* 11.5–16s: AI Streaming & Reading Time */}
      <Sequence from={348} durationInFrames={15}>
        <Audio src={staticFile('audio/sfx_typing.wav')} volume={0.40} />
      </Sequence>
      <Sequence from={366} durationInFrames={10}>
        <Audio src={staticFile('audio/sfx_tap.wav')} volume={0.50} />
      </Sequence>
      <Sequence from={382} durationInFrames={25}>
        <Audio src={staticFile('audio/sfx_ai_stream.wav')} volume={0.45} />
      </Sequence>

      {/* 16–18.5s: Retry, Correct Answer, & Confetti */}
      <Sequence from={480} durationInFrames={12}>
        <Audio src={staticFile('audio/sfx_whip.wav')} volume={0.45} />
      </Sequence>
      <Sequence from={504} durationInFrames={10}>
        <Audio src={staticFile('audio/sfx_tap.wav')} volume={0.48} />
      </Sequence>
      <Sequence from={517} durationInFrames={10}>
        <Audio src={staticFile('audio/sfx_tap.wav')} volume={0.50} />
      </Sequence>
      <Sequence from={522} durationInFrames={32}>
        <Audio src={staticFile('audio/sfx_success.wav')} volume={0.65} />
      </Sequence>

      {/* 18.5–21s: Score 80% Count-Up & Chips */}
      <Sequence from={555} durationInFrames={15}>
        <Audio src={staticFile('audio/sfx_slide.wav')} volume={0.38} />
      </Sequence>
      <Sequence from={564} durationInFrames={36}>
        <Audio src={staticFile('audio/sfx_counter.wav')} volume={0.55} />
      </Sequence>
      <Sequence from={574} durationInFrames={10}>
        <Audio src={staticFile('audio/sfx_chip_pop.wav')} volume={0.45} />
      </Sequence>
      <Sequence from={582} durationInFrames={10}>
        <Audio src={staticFile('audio/sfx_chip_pop.wav')} volume={0.42} />
      </Sequence>

      {/* 21–24s: Progress Analytics & Outro */}
      <Sequence from={630} durationInFrames={15}>
        <Audio src={staticFile('audio/sfx_slide.wav')} volume={0.38} />
      </Sequence>
      <Sequence from={670} durationInFrames={50}>
        <Audio src={staticFile('audio/sfx_outro.wav')} volume={0.65} />
      </Sequence>
    </>
  );
};
