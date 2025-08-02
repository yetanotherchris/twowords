# Use the official .NET 9 runtime as base image
FROM mcr.microsoft.com/dotnet/aspnet:9.0 AS base
WORKDIR /app
EXPOSE 8080
EXPOSE 8081

# Use the SDK image to build the application
FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
ARG BUILD_CONFIGURATION=Release
WORKDIR /src

# Copy csproj files and restore dependencies
COPY ["src/TwoWordsApi/TwoWordsApi.csproj", "src/TwoWordsApi/"]
COPY ["tests/TwoWordsApi.Tests/TwoWordsApi.Tests.csproj", "tests/TwoWordsApi.Tests/"]
COPY ["twowords.sln", "."]
RUN dotnet restore "src/TwoWordsApi/TwoWordsApi.csproj"

# Copy the entire source code including the zip file
COPY . .

WORKDIR "/src/src/TwoWordsApi"
RUN dotnet build "TwoWordsApi.csproj" -c $BUILD_CONFIGURATION -o /app/build

# Publish the application
FROM build AS publish
ARG BUILD_CONFIGURATION=Release
RUN dotnet publish "TwoWordsApi.csproj" -c $BUILD_CONFIGURATION -o /app/publish /p:UseAppHost=false

# Final stage - runtime image
FROM base AS final
WORKDIR /app

# Copy the published application
COPY --from=publish /app/publish .

# Copy the words.txt file from the source
# The WordMappingService expects it at /app/words.txt when DOTNET_RUNNING_IN_CONTAINER=true
COPY src/TwoWordsApi/words.txt ./words.txt

# Set environment variables
ENV ASPNETCORE_URLS=http://+:8080
ENV ASPNETCORE_ENVIRONMENT=Production
ENV DOTNET_RUNNING_IN_CONTAINER=true

ENTRYPOINT ["dotnet", "TwoWordsApi.dll"]
