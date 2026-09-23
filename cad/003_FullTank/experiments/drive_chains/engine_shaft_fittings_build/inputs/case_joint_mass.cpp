// Adaptive integration of exact BRep surfaces, using the installed OCC runtime.
#include <BRepTools.hxx>
#include <BRep_Builder.hxx>
#include <BRepGProp.hxx>
#include <GProp_GProps.hxx>
#include <TopoDS_Shape.hxx>
#include <iostream>
#include <iomanip>
int main(int argc,char** argv) {
    if(argc!=2) return 2;
    TopoDS_Shape shape;BRep_Builder builder;
    if(!BRepTools::Read(shape,argv[1],builder) || shape.IsNull()) return 3;
    GProp_GProps props;
    const double error=BRepGProp::VolumeProperties(shape,props,1e-12,true,false);
    const gp_Pnt center=props.CentreOfMass();
    std::cout << std::setprecision(17) << "{\"volume_mm3\":" << props.Mass()
        << ",\"estimated_relative_error\":" << error << ",\"center_mm\":["
        << center.X() << ',' << center.Y() << ',' << center.Z() << "]}\n";
    return 0;
}
