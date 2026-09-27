// Restricted surface integration for tubes and untrimmed curved patches.
// Nonplanar faces must have rectangular UV domains; planar trims use Green's theorem.
#include <BRepTools.hxx>
#include <BRep_Builder.hxx>
#include <BRep_Tool.hxx>
#include <BRepAdaptor_Surface.hxx>
#include <BRepAdaptor_Curve.hxx>
#include <BRepClass_FaceClassifier.hxx>
#include <BRepCheck_Analyzer.hxx>
#include <BRepGProp.hxx>
#include <GProp_GProps.hxx>
#include <Geom2d_Curve.hxx>
#include <Geom2d_BSplineCurve.hxx>
#include <Geom2d_BezierCurve.hxx>
#include <Geom2d_Line.hxx>
#include <Geom2d_TrimmedCurve.hxx>
#include <Geom_BSplineSurface.hxx>
#include <TopoDS.hxx>
#include <TopExp_Explorer.hxx>
#include <Standard_Version.hxx>
#include <gp_Pnt2d.hxx>
#include <algorithm>
#include <array>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <vector>

using Four=std::array<long double,4>;
struct Face {TopoDS_Face face; bool disk=false,plane=false; gp_Circ circle; gp_Ax3 planeAxes; double sign=1;
  double u0,u1,v0,v1; std::vector<double> us,vs;};

std::vector<std::pair<double,double>> gauss(int n) {
  std::vector<std::pair<double,double>> out;
  for(int i=1;i<=n;i++) {
    double z=std::cos(M_PI*(i-.25)/(n+.5)),pp=0;
    for(int k=0;k<30;k++) {
      double p1=1,p2=0;
      for(int j=1;j<=n;j++){double p3=p2;p2=p1;p1=((2*j-1)*z*p2-(j-1)*p3)/j;}
      pp=n*(z*p1-p2)/(z*z-1); double dz=p1/pp;z-=dz;if(std::abs(dz)<2e-16)break;
    }
    out.emplace_back(z,2/((1-z*z)*pp*pp));
  }
  return out;
}

bool rectangle(const Face& f) {
  const double tol=2e-7;
  for(TopExp_Explorer it(f.face,TopAbs_EDGE);it.More();it.Next()) {
    double lo,hi;auto c=BRep_Tool::CurveOnSurface(TopoDS::Edge(it.Current()),f.face,lo,hi);
    if(c.IsNull())return false;
    auto basis=c;
    while(!Handle(Geom2d_TrimmedCurve)::DownCast(basis).IsNull())
      basis=Handle(Geom2d_TrimmedCurve)::DownCast(basis)->BasisCurve();
    bool boundary=false;auto line=Handle(Geom2d_Line)::DownCast(basis);
    if(!line.IsNull()) {
      auto p=line->Location();auto d=line->Direction();
      boundary=(std::abs(d.X())<1e-12 && std::min(std::abs(p.X()-f.u0),std::abs(p.X()-f.u1))<tol)
        || (std::abs(d.Y())<1e-12 && std::min(std::abs(p.Y()-f.v0),std::abs(p.Y()-f.v1))<tol);
    } else {
      std::array<double,4> errors={0,0,0,0};int count=0;
      auto check=[&](gp_Pnt2d p,double weight){
        if(weight<=0)throw std::runtime_error("Nonpositive boundary weight");count++;
        errors[0]=std::max(errors[0],std::abs(p.X()-f.u0));errors[1]=std::max(errors[1],std::abs(p.X()-f.u1));
        errors[2]=std::max(errors[2],std::abs(p.Y()-f.v0));errors[3]=std::max(errors[3],std::abs(p.Y()-f.v1));};
      auto bs=Handle(Geom2d_BSplineCurve)::DownCast(basis);auto bz=Handle(Geom2d_BezierCurve)::DownCast(basis);
      if(!bs.IsNull())for(int k=1;k<=bs->NbPoles();k++)check(bs->Pole(k),bs->Weight(k));
      if(!bz.IsNull())for(int k=1;k<=bz->NbPoles();k++)check(bz->Pole(k),bz->Weight(k));
      boundary=count && *std::min_element(errors.begin(),errors.end())<tol;
    }
    if(!boundary){std::cerr<<"Pcurve support is not an iso-parametric rectangle boundary"<<std::endl;return false;}
    for(int i=0;i<=32;i++) {
      gp_Pnt2d p=c->Value(lo+(hi-lo)*i/32.);
      double error=std::min({std::abs(p.X()-f.u0),std::abs(p.X()-f.u1),
                             std::abs(p.Y()-f.v0),std::abs(p.Y()-f.v1)});
      if(error>tol){std::cerr<<"Boundary outside rectangle: "<<p.X()<<","<<p.Y()<<" error "<<error<<" bounds "<<f.u0<<","<<f.u1<<","<<f.v0<<","<<f.v1<<std::endl;return false;}
    }
  }
  for(int i=1;i<=5;i++)for(int j=1;j<=5;j++) {
    BRepClass_FaceClassifier classify(f.face,gp_Pnt2d(f.u0+(f.u1-f.u0)*i/6.,f.v0+(f.v1-f.v0)*j/6.),1e-9);
    if(classify.State()!=TopAbs_IN && classify.State()!=TopAbs_ON)return false;
  }
  return true;
}

Four integrate(const Face& f,int order,const gp_Pnt& origin) {
  Four sum={0,0,0,0};BRepAdaptor_Surface surface(f.face);
  if(f.disk) {
    double r=f.circle.Radius(),area=M_PI*r*r;gp_Vec c(origin,f.circle.Location());
    gp_Dir nd=f.planeAxes.Direction();gp_Vec n(nd);n*=f.sign;
    sum[0]=area*c.Dot(n)/3.;
    for(int i=1;i<=3;i++)sum[i]=area*n.Coord(i)*(c.Coord(i)*c.Coord(i)+r*r/4*(1-nd.Coord(i)*nd.Coord(i)))/2;
    return sum;
  }
  auto nodes=gauss(order);
  if(f.plane) {
    // Green's theorem integrates actual planar trimming curves, including
    // B-spline end caps. Oriented holes subtract material automatically.
    long double A=0,U=0,V=0,UU=0,UV=0,VV=0;
    TopoDS_Face forward=TopoDS::Face(f.face.Oriented(TopAbs_FORWARD));
    for(TopExp_Explorer it(forward,TopAbs_EDGE);it.More();it.Next()) {
      TopoDS_Edge e=TopoDS::Edge(it.Current());double lo,hi;
      auto c=BRep_Tool::CurveOnSurface(e,forward,lo,hi);
      if(c.IsNull())throw std::runtime_error("Missing planar boundary pcurve");
      double sign=e.Orientation()==TopAbs_REVERSED?-1:1;
      std::vector<double> spans={lo,hi};auto basis=c;
      while(!Handle(Geom2d_TrimmedCurve)::DownCast(basis).IsNull())
        basis=Handle(Geom2d_TrimmedCurve)::DownCast(basis)->BasisCurve();
      auto bs=Handle(Geom2d_BSplineCurve)::DownCast(basis);
      if(!bs.IsNull())for(int k=1;k<=bs->NbKnots();k++) {
        double knot=bs->Knot(k);
        if(bs->IsPeriodic()) {
          double period=bs->Period();int first=int(std::floor((lo-knot)/period));
          for(int n=first;knot+n*period<hi;n++)if(knot+n*period>lo)spans.push_back(knot+n*period);
        } else if(knot>lo && knot<hi)spans.push_back(knot);
      }
      std::sort(spans.begin(),spans.end());
      for(size_t i=1;i<spans.size();i++)for(auto tw:nodes) {
        double a=spans[i-1],b=spans[i],t=(a+b)/2+(b-a)/2*tw.first;
        gp_Pnt2d p;gp_Vec2d d;c->D1(t,p,d);
        // Use an orthonormal physical chart, also for certified affine
        // B-spline representations of planes produced by rigid STEP export.
        gp_Pnt xyz;gp_Vec su,sv;surface.D1(p.X(),p.Y(),xyz,su,sv);
        gp_Vec relative(f.planeAxes.Location(),xyz),derivative=su*d.X()+sv*d.Y();
        gp_Vec ex(f.planeAxes.XDirection()),ey(f.planeAxes.YDirection());
        long double w=tw.second*(b-a)/2*sign,u=relative.Dot(ex),v=relative.Dot(ey),
                    du=derivative.Dot(ex),dv=derivative.Dot(ey);
        A+=w*u*dv;U+=w*u*u*dv/2;V-=w*v*v*du/2;
        UU+=w*u*u*u*dv/3;UV+=w*u*u*v*dv/2;VV-=w*v*v*v*du/3;
      }
    }
    if(A<=0)throw std::runtime_error("Invalid oriented planar area");
    auto axes=f.planeAxes;gp_Vec ex(axes.XDirection()),ey(axes.YDirection());
    gp_Vec n=ex.Crossed(ey);n*=f.sign;gp_Vec c(origin,axes.Location());
    sum[0]=(A*c.Dot(n)+U*ex.Dot(n)+V*ey.Dot(n))/3;
    for(int i=1;i<=3;i++) {
      long double x=c.Coord(i),a=ex.Coord(i),b=ey.Coord(i);
      sum[i]=n.Coord(i)*(x*x*A+2*x*(a*U+b*V)+a*a*UU+2*a*b*UV+b*b*VV)/2;
    }
    return sum;
  }
  for(size_t i=1;i<f.us.size();i++)for(size_t j=1;j<f.vs.size();j++) {
    double a=f.us[i-1],b=f.us[i],c=f.vs[j-1],d=f.vs[j];
    for(auto uw:nodes)for(auto vw:nodes) {
      double u=(a+b)/2+(b-a)/2*uw.first,v=(c+d)/2+(d-c)/2*vw.first;
      gp_Pnt p;gp_Vec du,dv;surface.D1(u,v,p,du,dv);
      gp_Vec n=du.Crossed(dv);n*=f.sign;gp_Vec x(origin,p);
      long double w=uw.second*vw.second*(b-a)*(d-c)/4;
      sum[0]+=w*x.Dot(n)/3;
      for(int k=1;k<=3;k++)sum[k]+=w*x.Coord(k)*x.Coord(k)*n.Coord(k)/2;
    }
  }
  return sum;
}

int main(int argc,char** argv) {
  try {
    if(argc!=2)throw std::runtime_error("Expected BRep path");
    TopoDS_Shape shape;BRep_Builder builder;
    if(!BRepTools::Read(shape,argv[1],builder))throw std::runtime_error("BRep read failed");
    if(!BRepCheck_Analyzer(shape).IsValid())throw std::runtime_error("Invalid BRep");
    int solids=0;for(TopExp_Explorer it(shape,TopAbs_SOLID);it.More();it.Next())solids++;
    if(solids!=1)throw std::runtime_error("Expected one solid");
    GProp_GProps rough;BRepGProp::VolumeProperties(shape,rough);
    gp_Pnt origin=rough.CentreOfMass();std::vector<Face> faces;
    for(TopExp_Explorer it(shape,TopAbs_FACE);it.More();it.Next()) {
      Face f;f.face=TopoDS::Face(it.Current());f.sign=f.face.Orientation()==TopAbs_REVERSED?-1:1;
      BRepAdaptor_Surface s(f.face);BRepTools::UVBounds(f.face,f.u0,f.u1,f.v0,f.v1);
      f.plane=s.GetType()==GeomAbs_Plane;
      if(f.plane)f.planeAxes=s.Plane().Position();
      if(!f.plane && s.GetType()==GeomAbs_BSplineSurface) {
        // Only the exact affine 2x2 nonrational representation is admitted.
        // General planar-looking curved/truncated patches remain rejected.
        auto bs=s.BSpline();
        if(bs->UDegree()==1 && bs->VDegree()==1 && bs->NbUPoles()==2 && bs->NbVPoles()==2
           && !bs->IsURational() && !bs->IsVRational()) {
          gp_Vec u(bs->Pole(1,1),bs->Pole(2,1)),v(bs->Pole(1,1),bs->Pole(1,2));
          gp_Pnt opposite=bs->Pole(1,1).Translated(u+v);
          if(opposite.Distance(bs->Pole(2,2))<1e-9 && u.Crossed(v).Magnitude()>1e-12) {
            f.plane=true;f.planeAxes=gp_Ax3(bs->Pole(1,1),gp_Dir(u.Crossed(v)),gp_Dir(u));
          }
        }
      }
      if(f.plane) {
        int edges=0;TopoDS_Edge edge;
        for(TopExp_Explorer e(f.face,TopAbs_EDGE);e.More();e.Next()){edges++;edge=TopoDS::Edge(e.Current());}
        if(edges==1) {
          BRepAdaptor_Curve c(edge);
          if(c.GetType()==GeomAbs_Circle && std::abs(c.LastParameter()-c.FirstParameter()-2*M_PI)<1e-7) {
            f.disk=true;f.circle=c.Circle();
          }
        }
      }
      if(!f.plane && !rectangle(f)){std::cerr<<"Face index "<<faces.size()<<" type "<<s.GetType()<<std::endl;throw std::runtime_error("Nonrectangular curved surface trim");}
      f.us={f.u0,f.u1};f.vs={f.v0,f.v1};
      if(s.GetType()==GeomAbs_BSplineSurface) {
        auto bs=s.BSpline();
        for(int k=1;k<=bs->NbUKnots();k++)if(bs->UKnot(k)>f.u0 && bs->UKnot(k)<f.u1)f.us.push_back(bs->UKnot(k));
        for(int k=1;k<=bs->NbVKnots();k++)if(bs->VKnot(k)>f.v0 && bs->VKnot(k)<f.v1)f.vs.push_back(bs->VKnot(k));
      }
      std::sort(f.us.begin(),f.us.end());std::sort(f.vs.begin(),f.vs.end());faces.push_back(f);
    }
    std::vector<Four> previous;Four total={0,0,0,0};std::vector<double> errors;
    std::vector<Four> totals;
    for(int order:{16,32,64}) {
      std::vector<Four> current;total={0,0,0,0};Four error={0,0,0,0};
      for(size_t i=0;i<faces.size();i++) {
        auto one=integrate(faces[i],order,origin);current.push_back(one);
        for(int j=0;j<4;j++){total[j]+=one[j];if(!previous.empty())error[j]+=std::abs(one[j]-previous[i][j]);}
      }
      if(!previous.empty()) {
        double scaled=double(error[0]/std::abs(total[0]));
        // Include first-moment convergence, normalized by a conservative length.
        double length=std::max(1.,std::cbrt(std::abs(double(total[0]))));
        for(int j=1;j<4;j++)scaled=std::max(scaled,double(error[j]/(std::abs(total[0])*length)));
        errors.push_back(scaled);totals.push_back(total);
      }
      previous=current;
    }
    std::cout<<std::setprecision(17)<<"{\"occ\":\""<<OCC_VERSION_COMPLETE<<"\",\"certified_faces\":"<<faces.size()
      <<",\"algorithm\":\"divergence theorem; rectangular curved UV patches and planar Green boundary integrals; knot-span Gauss 16/32/64\",\"results\":[";
    for(int k=0;k<2;k++) {
      if(k)std::cout<<",";auto t=totals[k];
      std::cout<<"{\"requested_error\":"<<(k?1e-12:1e-10)<<",\"reported_error\":"<<errors[k]<<",\"volume\":"<<double(t[0])<<",\"centroid\":[";
      for(int i=1;i<=3;i++){if(i>1)std::cout<<",";std::cout<<origin.Coord(i)+double(t[i]/t[0]);}
      std::cout<<"]}";
    }
    std::cout<<"]}"<<std::endl;
  } catch(const std::exception& e){std::cerr<<e.what()<<std::endl;return 1;}
}
