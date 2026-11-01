# Interaction and accessibility branches

Load for forms, dialogs, dropdowns/menus, keyboard-rich widgets, focus changes, or asynchronous status updates.

- **Forms:** each input has a programmatic label; errors identify the affected field and are perceivable; native validation and existing form semantics take precedence. Verify keyboard submission, busy/disabled transitions and repeat submissions when data mutation is involved.
- **Dialogs:** verify focus entry, containment as appropriate to the existing dialog solution, Escape/close behavior where permitted, focus return, and an accessible name. Preserve existing modal library semantics rather than inventing custom keyboard behavior.
- **Menus and composite controls:** prefer native controls or existing tested primitives. Check keyboard navigation, selected/expanded state and focus behavior against the component's actual interaction model.
- **Dynamic content:** loading and errors are observable; announce important changes where appropriate without noisy repeated announcements. Avoid stale async updates after unmount or request supersession when relevant.
- **Links/buttons:** navigational actions use links; actions use buttons. Accessible names describe actions; icons alone need a name. Disabled states must not create unusable navigation traps.
- **Motion/contrast:** honor existing reduced-motion and color/contrast contracts when touched. Do not claim full WCAG compliance from automated checks alone.

If the project uses a recognized accessible component library, prefer its supported composition and documented patterns. Changes to shared primitives warrant broader keyboard/regression checks.
