# For the `[headyaw]` test: BL1GOTYVR restores the view after drawing

From: `/gr`, 2026-10-04. Applies to dossier §9h (the yaw test, built the same day).

- Borderlands 1's UE3 VR mod saves the controller's view (`CalcViewLocation`, `CalcViewRotation`,
  `CachedFOVAngle`), writes the head pose, calls `GameViewportClient::Draw` once, then **restores** the saved
  values `[reported 2026-10-04]`. Our hook writes `CameraCache.POV` yaw after the camera loop and never restores it.
- Suggested addition to §9h's outcome table: if the launch shows the walking direction turning or the yaw spinning,
  the fix is a matching restore after the frame is drawn, not a different write point `[hypothesis]`.
- Also from the same source, already in this lane: calling `Draw` twice per frame corrupted the heap in that build.
- Topic: `external-research/topics/2026-10-04-bl1gotyvr-writes-the-view-just-before-draw-and-restores-it.md`.
