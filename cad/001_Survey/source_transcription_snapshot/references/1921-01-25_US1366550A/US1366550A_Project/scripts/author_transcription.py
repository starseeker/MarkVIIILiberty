"""Reviewed against the supplied USPTO scan, preserving its printed line sequence."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
TEXT={
'3L': '''To all whom it may concern:
Be it known that I, HERBERT W. ALDEN,
lieutenant colonel, Ordnance Dept., United
States Army, a citizen of the United States,
stationed at Washington, District of Co-
lumbia, have invented an Improvement in
Tanks, of which the following is a specifi-
cation.

The invention described herein may be
used by the Government, or any of its offi-
cers or employees in prosecution of work for
the Government, or by any other person in
the United States, without payment of any
royalty thereon.

As military “tanks,” so called, have hereto-
fore been constructed, so far as I am aware,
the sponson has been an immovable and ir-
removable structure, which projects from
the side of the tank. In many instances, the
sponson forms an obstruction to the passage
of the tank, because (assuming a hypotheti-
cal case) it may be desired to drive the tank
through a narrow ravine (artificial or natu-
ral) which is of insufficient width to permit
the passage of the tank with such projecting
sponson, but which is of a width which would
permit the passage of a tank if such spon-
son were not present.

The principal object of my invention is,
therefore, to provide a tank with a movable,
projecting sponson, whereby a tank equipped
with my invention may travel where tanks
of proportionate size, but which are pro-
vided with immovable sponsons, cannot go,
and thus accomplish results which it is im-
possible to attain with such other tanks.

With these objects in view, and others
appearing as the specification proceeds and
the nature of the invention is more fully dis-
closed, the invention resides, broadly and
generally stated, in a tank provided with a
movable sponson and, more specifically, in a
tank provided with a sponson adapted to
swing on a pivot from a position normally
outside the tank to a position therewithin,
to meet the exigencies of a particular situa-
tion.

The invention also resides in various struc-
tural refinements, tributary to the basic con-
struction just referred to, which go to make
up the ultimate perfection of the gun as an
entirety.

The accompanying drawings disclose an
exemplary concrete embodiment of the un-''',
'3R': '''derlying principles of my invention. Like
reference characters identify corresponding
parts throughout the several views, which
latter may be briefly described as follows:

Figure 1 is a fragmentary longitudinal
vertical sectional view of a tank equipped
with a sponson constructed in accordance
with my invention;

Fig. 2 is a cross sectional view on the line
2—2, Fig. 1; and

Fig. 3 is a horizontal sectional view
through the sponson.

Referring, now, in detail to the drawings:

The sponson 1 is, in contra-distinction to
the ordinary construction of sponsons, a
movable body and, for this purpose, is ap-
propriately supported upon hinges 2—2 car-
ried by the tank frame 3, whereby the spon-
son may swing in a horizontal plane from
the normal full-line position thereof to the
dotted line position shown in Fig. 3, so as
to occupy a position entirely within the tank.

Suitable means are provided for securing
the sponson in its normal position exteriorly
of the tank body or frame and while, con-
ceivably, such means may take various
forms, I have disclosed an exemplary means
that may be used, and which I will now de-
scribe.

Carried by the marginal edge of that side
of the sponson which is opposite the pivotal
side thereof is an angle iron or bar 4, one
of the flanges of such bar resting against
the side of the sponson and the other flange
constituting a lip which normally bears
against the inner surface of the side wall 3
of the tank. The angle iron 4 thus also
serves the purpose of limiting the outward
movement of the sponson. Passing through
the said lip and through said wall 3 and pref-
erably through a strengthening member 5,
which may be an angle iron, is a plurality
of securing means, such as screws 6. It will
be noted that, by the provisions of an angle
iron 4, an effective closure is provided be-
tween the side of the sponson and the ad-
jacent edge of the wall 3 of the tank, against
entrance to the tank of dirt, moisture, etc.

The top of the sponson 1, in the normal
position of the latter, is extended so as to
project into the tank as shown in Fig. 2, thus
forming, as it were, a lip 7; and carried on
top of this lip is an angle iron or bar 8, one
of the flanges thereof bearing against the''',
'4L': '''inner surface of the vertical wall of said
tank, adjacent the opening through which
the sponson projects. Said angle bar 8 may,
obviously, of course, if desired, be secured
to the front wall of the tank, instead of to
the lip 7. This angle bar 8 affords a closure
against entrance to the tank of dirt and
moisture.

Adjacent the hinges 2, suitable means are
provided for preventing the entrance to the
tank of dirt and moisture, and in this in-
stance, such means comprises an angle bar 9
carried by the sponson and contacting, in the
normal position of the sponson, with a sec-
ond angle bar 10 carried by the wall 3 of the
tank.

The sponson 1 may carry a chamber 13 for
the storage of shells. For the sake of light-
ness, the chamber is provided with numer-
ous perforations 14.

While I have, in compliance with the Re-
vised Statutes of the United States, described
with great particularity one form of embodi-
ment of my invention, it is to be understood
that many changes will suggest themselves,
particularly to those skilled in the art to
which the invention pertains, and that all
such changes as come within the scope of the
appended claims constitute no departure
from the spirit of the invention.

Having thus fully described my invention,
what I claim as new and desire to secure by
Letters Patent is:

1. In a military tank, a sponson normally
disposed exteriorly of the tank and movable
through a wall of the tank to a position with-
in the tank, the sponson closing the wall
when in normal position.

2. In a military tank, a pivotally mounted
sponson normally disposed exteriorly of the
tank and movable through an opening in the
tank to a position therewithin, the sponson
forming a closure for the opening when in
normal position.

3. In a military tank, a sponson normally
operating through and forming a closure for
an opening in a wall of the tank, normally
disposed exteriorly thereof and movable to a''',
'4R': '''position therewithin, and means for prevent-
ing movement of said sponson when posi-
tioned exteriorly of the tank.

4. In a military tank, a sponson operating
through and forming a closure for an open-
ing therein normally projecting therefrom
and movable to a position therewithin, and
means for securing said sponson in its nor-
mal position, including a member carried by
said sponson and limiting outward move-
ment thereof.

5. In a military tank, a sponson operating
through and forming a closure for an open-
ing in the tank, said sponson normally pro-
jecting therefrom and movable to a position
therewithin, and means for securing said
sponson in its normal position, including an
angle iron carried by said sponson and limit-
ing outward movement thereof.

6. In a military tank, a sponson movably
operating through and forming a closure for
an opening in the tank, said sponson nor-
mally projecting therefrom and movable to
a position therewithin, means for securing
said sponson in its normal position, includ-
ing an angle iron carried by said sponson and
limiting outward movement thereof, and se-
curing means passing through said angle
iron and the wall of said tank.

7. A disappearing sponson for tanks piv-
oted at its forward end and operating
through an opening in a wall of the tank,
and having a protecting shield forming a
complete closure to the opening when the
sponson is in normal position.

8. A disappearing sponson for tanks or the
like adapted to operate through an opening
in the side of said tank and supporting a
piece of ordnance and forming a closure to
the tank when in its outermost position.

9. A disappearing combination sponson
and gun mount adapted to operate through
an opening in an armored wall, pivoted at
its forward edge and forming a closure in
the wall when swung to its outermost po-
sition.'''
}
OUT={}
for key,txt in TEXT.items():
    rows=[]
    paras=txt.split('\n\n')
    for ip,para in enumerate(paras):
        lines=para.splitlines()
        for i,t in enumerate(lines):
            # Column openings that continue preceding columns are unindented.
            start=i==0 and (ip>0 or key=='3L')
            if key=='3L' and ip==0:start=i==1
            rows.append(dict(text=t,indent=start,last=i==len(lines)-1))
    # A broken paragraph is not justified as a terminal line.
    if key!='4R':rows[-1]['last']=False
    OUT[key]=rows
    print(key,len(rows))
(ROOT/'data/reviewed_transcription.json').write_text(json.dumps(OUT,ensure_ascii=False,indent=2))
(ROOT/'data/transcription_lines.txt').write_text('\n\n'.join('PAGE / COLUMN '+k+'\n'+v for k,v in TEXT.items())+'\n')
