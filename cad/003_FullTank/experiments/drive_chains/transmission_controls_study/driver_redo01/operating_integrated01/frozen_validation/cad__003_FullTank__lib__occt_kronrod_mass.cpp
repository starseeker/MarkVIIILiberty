// Knot-span-aware integration of an unchanged closed BRep.
#include <BRepTools.hxx>
#include <BRep_Builder.hxx>
#include <BRepGProp.hxx>
#include <GProp_GProps.hxx>
#include <TopoDS_Shape.hxx>
#include <Standard_Version.hxx>
#include <iostream>
#include <iomanip>
int main(int argc,char**argv){
 if(argc!=2)return 2;
 TopoDS_Shape shape;BRep_Builder builder;
 if(!BRepTools::Read(shape,argv[1],builder))return 3;
 std::cout<<std::setprecision(17)<<"{\"occ\":\""<<OCC_VERSION_COMPLETE<<"\",\"results\":[";
 bool first=true;
 for(double eps:{1e-10,1e-12}){
  GProp_GProps props;
  double err=BRepGProp::VolumePropertiesGK(shape,props,eps,true,true,true,false,false);
  auto p=props.CentreOfMass();
  if(!first)std::cout<<",";first=false;
  std::cout<<"{\"requested_error\":"<<eps<<",\"reported_error\":"<<err
   <<",\"volume\":"<<props.Mass()<<",\"centroid\":["<<p.X()<<","<<p.Y()<<","<<p.Z()<<"]}";
 }
 std::cout<<"]}\n";
}
