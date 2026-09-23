#include <BRepTools.hxx>
#include <BRep_Builder.hxx>
#include <BRepGProp.hxx>
#include <GProp_GProps.hxx>
#include <TopoDS_Shape.hxx>
#include <iostream>
#include <iomanip>
int main(int argc,char** argv){
 TopoDS_Shape s;BRep_Builder b;if(argc!=2||!BRepTools::Read(s,argv[1],b))return 2;
 for(double eps:{1e-10,1e-12,1e-14})for(bool gk:{false,true}){
 GProp_GProps p;double e=gk?BRepGProp::VolumePropertiesGK(s,p,eps,true,true,true,false,false):BRepGProp::VolumeProperties(s,p,eps,true,false);
 auto c=p.CentreOfMass();std::cout<<std::setprecision(17)<<gk<<" "<<eps<<" "<<e<<" "<<p.Mass()<<" "<<c.X()<<" "<<c.Y()<<" "<<c.Z()<<std::endl;
 }
}
