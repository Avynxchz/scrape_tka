import React from 'react';
import { Composition } from 'remotion';
import { Showreel } from './Showreel';
import { DUR, FPS, H, W } from './lib';

export const RemotionRoot: React.FC = () => (
  <Composition id="Showreel" component={Showreel} durationInFrames={DUR} fps={FPS} width={W} height={H} />
);
