/* Depth-buffer rasterization of native CAD preview triangles. No CAD geometry
 * is simplified or modified here; this replaces the equivalent NumPy loop. */
#include <math.h>
#include <stddef.h>
#include <stdint.h>

void rasterize(int width, int height, size_t count, const double *xyz,
               const uint8_t *colors, uint8_t *pixels, double *depth) {
    for (size_t triangle=0; triangle<count; ++triangle) {
        const double *v=xyz+triangle*9;
        double ax=v[0], ay=v[1], az=v[2], bx=v[3], by=v[4], bz=v[5],
               cx=v[6], cy=v[7], cz=v[8];
        int x0=(int)fmax(0,fmin(ax,fmin(bx,cx)));
        int x1=(int)fmin(width,(int)fmax(ax,fmax(bx,cx))+2);
        int y0=(int)fmax(0,fmin(ay,fmin(by,cy)));
        int y1=(int)fmin(height,(int)fmax(ay,fmax(by,cy))+2);
        double denominator=(by-cy)*(ax-cx)+(cx-bx)*(ay-cy);
        if (fabs(denominator)<1e-10 || x0>=x1 || y0>=y1) continue;
        for (int y=y0; y<y1; ++y) {
            for (int x=x0; x<x1; ++x) {
                double px=x+0.5, py=y+0.5;
                double a=((by-cy)*(px-cx)+(cx-bx)*(py-cy))/denominator;
                double b=((cy-ay)*(px-cx)+(ax-cx)*(py-cy))/denominator;
                double c=1-a-b;
                if (a < -1e-7 || b < -1e-7 || c < -1e-7) continue;
                double z=a*az+b*bz+c*cz;
                size_t index=(size_t)y*width+x;
                if (z>depth[index]) {
                    depth[index]=z;
                    for (int channel=0; channel<3; ++channel)
                        pixels[index*3+channel]=colors[triangle*3+channel];
                }
            }
        }
    }
}
